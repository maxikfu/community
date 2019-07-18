from google.cloud import firestore
import google.cloud.exceptions
from datetime import datetime
import pytz
utc = pytz.UTC


def get(collection, document):
    """
    Get fields from firebase collection and document
    :param collection: collection name in firebase
    :param document: document name in firebase
    :return: returns document fields as dictionary
    """
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
    """
    Update document fields in firebase
    :param collection: collection name in firebase
    :param document: document name in firebase
    :param new_value: Dictionary of fields as a key and new values
    """
    db = firestore.Client()
    # [START update_doc]
    doc_ref = db.collection(collection).document(document)
    # Set the capital field
    doc_ref.update(new_value)
    # [END update_doc]


def add(collection, document, fields):
    """
    Create new document in the collection (or new collection)
    :param collection:  name of the collection
    :param document:  name of the document
    :param fields: document fields
    """
    # [START add]
    db = firestore.Client()
    # Add a new doc in collection with ID "document"
    db.collection(collection).document(document).set(fields)
    # [END add]


def delete(collection, document):
    """
    Delete single document in the collection by ID
    :param collection: collection name
    :param document: document name
    """
    db = firestore.Client()
    # [START delete_single_doc]
    db.collection(collection).document(document).delete()
    # [END delete_single_doc]


def coll_content(collection):
    """
    List all document ID in the collection
    :param collection: collection name
    :return: set of document IDs
    """
    db = firestore.Client()
    # [START]
    coll_ref = db.collection(collection)
    docs = coll_ref.get()
    res = set()
    for doc in docs:
        res.add(doc.id)
    return res
    # [END]


if __name__ == '__main__':
    print(coll_content('db'))

