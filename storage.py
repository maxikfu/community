from google.cloud import firestore
import google.cloud.exceptions
from datetime import datetime
import pytz
utc = pytz.UTC


def get_doc():
    db = firestore.Client()
    # [START get_check_exists]
    doc_ref = db.collection(u'db').document(u'news')
    try:
        doc = doc_ref.get()
        return doc.to_dict()['threshold']
    except google.cloud.exceptions.NotFound:
        print(u'No such document!')
    # [END get_check_exists]


def update_doc(new_value):
    db = firestore.Client()
    # [START update_doc]
    doc_ref = db.collection(u'db').document(u'news')

    # Set the capital field
    doc_ref.update({u'threshold': new_value})
    # [END update_doc]


if __name__ == '__main__':
    store = get_doc()
    n = utc.localize(datetime.now())
    print(store)
    print(n)
    print(store > n)
