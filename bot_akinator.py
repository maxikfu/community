import akinator
import json
from datetime import datetime
import storage

AKINATOR_COLLECTION = 'akinator'


def quick_game():
    aki = akinator.Akinator()
    q = aki.start_game()
    while aki.progression <= 85:
        a = input(q + "\n\t")
        if a == "b":
            try:
                q = aki.back()
            except akinator.CantGoBackAnyFurther:
                pass
        else:
            q = aki.answer(a)
    aki.win()
    correct = input(f"It's {aki.name} ({aki.description})! Was I correct?\n{aki.picture}\n\t")
    if correct.lower() == "yes" or correct.lower() == "y":
        print("Yay\n")
    else:
        print("Oof\n")


def game(from_id, text, time):
    if str(from_id) in storage.coll_content(AKINATOR_COLLECTION):  # resuming the game
        fields = storage.get(AKINATOR_COLLECTION, str(from_id))  # getting saved game
        aki = load(fields)  # creating akinator instance
        response = aki.answer(text)  # passing users answer to akinator
        #  checking if we are close to make prediction
        if aki.progression <= 85:  # we can make a prediction
            aki.win()
            response = {'text': "It's {} ({})! Was I correct?".format(aki.name, aki.description)}
            if aki.picture:
                response['picture_url'] = aki.picture
            storage.delete(AKINATOR_COLLECTION, str(from_id))  # deleting document when the game is over
        else:  # we need to save current progression
            aki.last_active = time
            d = dump(aki)
            storage.update(AKINATOR_COLLECTION, str(from_id), d)
    else:  # creating the new game
        aki = akinator.Akinator()
        # starting game and asking user first question
        response = aki.start_game()
        # save current progress
        aki.last_active = time
        storage.add(AKINATOR_COLLECTION, str(from_id), dump(aki))
    return response


def dump(entity):
    """
    Converts current object to json string
    :param entity:
    :return: json representation of the dictionary
    """
    d = {'server': entity.server, 'session': entity.session, 'signature': entity.signature, 'uid': entity.uid,
         'frontaddr': entity.frontaddr, 'question': entity.question, 'progression': entity.progression,
         'step': entity.step, 'last_active': datetime.now()}
    return d


def load(d):
    """
    Converts dictionary to entity
    :param d: dictionary with fields
    :return: akinator class object
    """
    entity = akinator.Akinator()
    entity.server = d['server']
    entity.step = d['step']
    entity.progression = d['progression']
    entity.question = d['question']
    entity.frontaddr = d['frontaddr']
    entity.uid = d['uid']
    entity.signature = d['signature']
    entity.session = d['session']
    entity.last_active = d['last_active']
    return entity


if __name__ == '__main__':
    r = game(491551942, 'Akinator', datetime.now())



