# transactions.py

import pandas as pd

class TransactionProcessor:

    def __init__(self):
        pass

    def create_transaction(self,
                           amount,
                           oldbalanceOrg,
                           newbalanceOrig,
                           oldbalanceDest,
                           newbalanceDest,
                           transaction_type,
                           sender_bank,
                           receiver_bank,
                           currency,
                           hour):

        transaction = {
            "amount": amount,
            "oldbalanceOrg": oldbalanceOrg,
            "newbalanceOrig": newbalanceOrig,
            "oldbalanceDest": oldbalanceDest,
            "newbalanceDest": newbalanceDest,
            "transaction_type": transaction_type,
            "sender_bank": sender_bank,
            "receiver_bank": receiver_bank,
            "currency": currency,
            "hour": hour
        }

        return pd.DataFrame([transaction])