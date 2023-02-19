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
| Method | URL              | Payload                                                      | Response                            |
|--------|------------------|--------------------------------------------------------------|-------------------------------------|
| GET    | /user/[name]     | Ø                                                            | {'user': userinfo}                  | 
| POST   | /add             | {'user': name}                                               | New user object                     |
| POST   | /transaction     | {'creditor': name, <br/>'debtor': name, <br/>'value': value} | Two user objects                    |

### Example requests
#### Add user
```
{
    "name": "Adam"
}
```
```
{
    "name": "Petr"
}
```
#### Add transaction
```
{
    "creditor": "Adam",
    "debtor": "Petr",
    "amount": 42
}
```
