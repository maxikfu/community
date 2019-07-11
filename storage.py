import datetime
from google.cloud import firestore
import google.cloud.exceptions


def get_data():
    db = firestore.Client()
    # [START get_check_exists]
    doc_ref = db.collection(u'db').document(u'news')

    try:
        doc = doc_ref.get()
        print(u'Document data: {}'.format(doc.to_dict()))
    except google.cloud.exceptions.NotFound:
        print(u'No such document!')
    # [END get_check_exists]


if __name__ == '__main__':
    get_data()
