"""Generate Markov text from text files."""
import twitter
import os
from random import choice
import sys


def open_and_read_file(file_paths):
    """Take file path as string; return text as string.

    Takes a string that is a file path, opens the file, and turns
    the file's contents as one string of text.
    """
    text_string = ""
    for file_path in file_paths:
        with open(file_path) as long_string:
            text_string = text_string + long_string.read()

    return text_string


def make_chains(text_string, number_words):
    """Take input text as string; return dictionary of Markov chains.

    A chain will be a key that consists of a tuple of (word1, word2)
    and the value would be a list of the word(s) that follow those two
    words in the input text.

    For example:

        >>> chains = make_chains("hi there mary hi there juanita")

    Each bigram (except the last) will be a key in chains:

        >>> sorted(chains.keys())
        [('hi', 'there'), ('mary', 'hi'), ('there', 'mary')]

    Each item in chains is a list of all possible following words:

        >>> chains[('hi', 'there')]
        ['mary', 'juanita']

        >>> chains[('there','juanita')]
        [None]
    """

    chains = {}
    text_list = text_string.split()

    for i in range(len(text_list)-number_words):
        word_combo = tuple(text_list[i:i+number_words])
        chains[word_combo] = chains.get(word_combo, []) + [text_list[i+number_words]]
        # if word_combo in chains.keys():
        #     chains[word_combo].append(text_list[i+2])
        # else:
        #     chains[word_combo] = [text_list[i+2]]

    return chains


def make_text(chains, number_words):
    """Return text from chains."""

    # from tuple / link key
    # randomly pick an item from its list of values
    current_key = choice(chains.keys())
    # while first word in key is not proper, keep picking a random key.
    while current_key[0].title() != current_key[0] or current_key[0] == "--":
        current_key = choice(chains.keys())

    words = list(current_key)
    current_length = len(" ".join(words))
    # adds last number_words of the k-v pair as new current key
    # do until the key doesn't exist
    while current_key in chains.keys() and current_length <= 132:  # w/o hashtag
        last_word = choice(chains[current_key])
        words.append(last_word)
        current_length = len(" ".join(words))
        current_key = tuple(words[-number_words:])
    return " ".join(words)


def output_file(random_text):
    """Create/edit an output file, adding text input to the file.

    Arg:
    Param (string): a random string of data

    Returns nothing
    """
    output = open("markov-story.out", "a")
    output.write(random_text + "\n\n")
    output.close()
    print "Your text is now saved into the output file markov-story."
    return random_text


def give_user_choice_of_ngrams(text_string):
    """Shows n-grams from 2-10 and prompts user to select one to return."""

    # Prompt user to choose punctuation to end at. Default is period
    punct_choice = raw_input("Do you want to end with '.' or '?' \n")
    if punct_choice not in [".", "?"]:
        print "Default is looking for something that ends with ."
        punct_choice = "."

    # create dictionary of all ngram options and print so the user can choose.
    ngram_options = {}
    for i in range(2, 11):
        ngram_chains = make_chains(text_string, i)
        ngram_options[i] = make_text(ngram_chains, i)

        #truncate to specified limit (for Twitter: 140 chars), ends punct choice
        ngram_options[i] = truncate_chars(ngram_options[i], punct_choice, i,
                                          ngram_chains, text_string)

        print "This is a story from a {}-gram:".format(i)
        print "{}".format(ngram_options[i])
        print "-------------------"

    # prompt user to select which n-gram they like
    # validate user input for range and integer
    print "Which ngram do you want to save?"
    while True:
        user_choice = raw_input("Enter a number between 2 and 10?\n")
        try:
            user_choice = int(user_choice)
        except ValueError:
            print "You need to enter a number (between 2 and 10). Try again!"
            continue
        if user_choice not in range(2, 11):
            print "You did not enter a number between 2 and 10, try again."
            continue
        break
    print "You selected {}-gram.".format(user_choice)

    return ngram_options[user_choice]


def truncate_chars(ngram, punct, num, chains, input_text):
    """ given a string, and punctuation, truncate up until the last punct
    Rerun the random story generation if there is no punct in the story
    Add a char limit of 140 """
    while True:
        for index in reversed(range(0, min(len(ngram), 132))):
            if ngram[index] == punct:
                if is_original(ngram[:index+1], input_text.rstrip()):
                    return ngram[:index+1]
        ngram = make_text(chains, num)


def is_original(ngram, input_text):
    """ checks if ngram is part of original text """
    input_text = input_text.replace("\n", " ")
    return ngram.rstrip() not in input_text.rstrip()


def twitter_request(input_text):
    """Promps user if they want to publish a story as a tweet.
    Gives them the option to keep posting new storys as tweets.
    Returns nothing"""
    while True:
        story = get_story(input_text)
        story = story + "#hbada17"
        print "Here is your story to tweet: \n '{}'".format(story)
        print "You can either publish (y), not publish and get a new tweet (n)"
        print "or you can quit (q)."
        user_answer = raw_input("Enter y, n, or q:\n")
        if user_answer.lower() not in ["y", "n"]:
            print "BYE!!"
            break
        elif user_answer.lower().startswith("y"):
            twitter_post(story)
            user_input = raw_input("Do you want to tweet again (y/n)?\n")
            if user_input.lower().startswith("y"):
                continue
            else:
                print "THANKS BYE"
                break
        elif user_answer.lower().startswith("n"):
            print "Okay, we'll get a different story for you to tweet."
            continue


def twitter_post(tweet):
    """ Interacts with Twitter API to publish posts """
    api = twitter.Api(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                      consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                      access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    status = api.PostUpdate(tweet)
    print status.text


def get_story(input_text):
    """ given an input text, calls functions to return Markov story
    Also save a copy to an output_file."""
    user_choice = give_user_choice_of_ngrams(input_text)
    story = output_file(user_choice)
    return story


input_path = sys.argv[1:]
# Open the file and turn it into one long string
input_text = open_and_read_file(input_path)
twitter_request(input_text)
# not using below with new feature adds
# number_words = 2
# # Get a Markov chain
# chains = make_chains(input_text, number_words)
# # Produce random text
# random_text = make_text(chains, number_words)
