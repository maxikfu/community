from google.cloud import firestore
import google.cloud.exceptions
from datetime import datetime
import pytz
utc = pytz.UTC


def get(collection, document):
    db = firestore.Client()
    # [START get_check_exists]
    doc_ref = db.collection(collection).document(document)
    try:
        doc = doc_ref.get()
        return doc.to_dict()
    except google.cloud.exceptions.NotFound:
        return u'No such document!'
    # [END get_check_exists]


def update(collection, document, new_value):
    db = firestore.Client()
    # [START update_doc]
    doc_ref = db.collection(collection).document(document)
    # Set the capital field
    doc_ref.update(new_value)
    # [END update_doc]


if __name__ == '__main__':
    store = get()
    print(store)

