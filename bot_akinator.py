import akinator
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


def game(from_id, text, time, returning):
    if text.lower() == 'stop':  # deleting the saved game
        storage.delete(AKINATOR_COLLECTION, str(from_id))
        return {"text": "Thank you for playing! If you want to play again just type and send Akinator!",
                "image_url": None, 'win': False}
    if returning:  # resuming the game
        fields = storage.get(AKINATOR_COLLECTION, str(from_id))  # getting saved game
        aki = load(fields)  # creating akinator instance
        if text.lower() in ['back', 'b']:  # we need to go back
            try:
                response = {"text": aki.back(), "image_url": None, 'win': False}
                aki.last_active = time
                storage.update(AKINATOR_COLLECTION, str(from_id), dump(aki))
                return response
            except akinator.exceptions.CantGoBackAnyFurther:
                return {"text": "Cannot go back! If you want to stop send Stop", "image_url": None, 'win': False}
        try:
            response = {"text": aki.answer(text), "image_url": None, 'win': False}  # passing users answer to akinator
        except akinator.exceptions.InvalidAnswerError:
            return {"text": """You put "{}", which is an invalid answer.
                The answer must be one of these:
                    - "yes" OR "y" OR "0" for YES
                    - "no" OR "n" OR "1" for NO
                    - "i" OR "idk" OR "i dont know" OR "i don't know" OR "2" for I DON'T KNOW
                    - "probably" OR "p" OR "3" for PROBABLY
                    - "probably not" OR "pn" OR "4" for PROBABLY NOT
                If you want to stop playing send word Stop.
                """.format(text)}
        #  checking if we are close to make prediction
        if aki.progression >= 85:  # we can make a prediction
            aki.win()
            response = {'text': "It's {} ({})!".format(aki.name, aki.description), 'win': True}
            if aki.picture:
                response['image_url'] = aki.picture
            storage.delete(AKINATOR_COLLECTION, str(from_id))  # deleting document when the game is over
        else:  # we need to save current progression
            aki.last_active = time
            d = dump(aki)
            storage.update(AKINATOR_COLLECTION, str(from_id), d)
    else:  # creating the new game
        aki = akinator.Akinator()
        # starting game and asking user first question
        response = {"text": aki.start_game(), "image_url": None, 'win': False}
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
    # r = game(491551942, 'Akinator', datetime.now())
    quick_game()


