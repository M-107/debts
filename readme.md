# Debts API
 View or add debts to and from users, add users, add transactions (debts)

### User object:
```json
{
    "name": "Username1",
    "owes_to": {
        "Creditorname2": 42,
        "Creditorname3": 4.2
    },
    "owed_by": {
        "Debtorname2": 12,
        "Debtorname4": 6
    },
    "sum": "<sum(owed_by) - sum(owes_to)>"
}
```
### Methods:
| Method | URL          | Payload                                                      | Response           | Response payload |
|--------|--------------|--------------------------------------------------------------|--------------------|------------------|
| GET    | /user/[name] | Ø                                                            | {'user': userinfo} | Ø                |
| POST   | /add         | {'user': name}                                               | Ø                  | New user object  |
| POST   | /transaction | {'creditor': name, <br/>'debtor': name, <br/>'value': value} | Ø                  | Two user objects |
