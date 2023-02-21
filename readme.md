# Debts API
View or add debts to and from users, add users, add transactions (debts)
 
*Run init_db before first launch. </br>
Then run start_server for each launch.*

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
| Method | URL          | Payload                                                      | Response                           |
|--------|--------------|--------------------------------------------------------------|------------------------------------|
| GET    | /all_users/  | Ø                                                            | {"all_users": all users` info}     |
| GET    | /user/[name] | Ø                                                            | {"user": user info}                | 
| POST   | /add         | {"name": name}                                               | New user object                    |
| POST   | /transaction | {"creditor": name, <br/>"debtor": name, <br/>"value": value} | Two user objects (ordered by name) |

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