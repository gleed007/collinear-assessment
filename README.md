# FastAPI Auth Custom Code

### Pre-requisites

- Python 3.10+

### Instructions to run the project

- pip3 install -r requirements.txt
- uvicorn main:app --reload

### Api routes

This project contains the code for creating the below four apis
| API Endpoint | Description |
| --- | --- |
| `/auth` | Create new user account |
| `/auth/token` | Login and get JWT Token |
| `/auth/refresh` | Refresh JWT Token |
| `/users/me` | Get Authenticated User Detail |
| `/users/datasets/followed` | Get Datasets Followed by Authenticated User |
| `/datasets` | Get Datasets pre seeded in Db |
| `/datasets/{dataset_id}/follow` | Follow a dataset |
| `/datasets/{dataset_name}` | Get paginated data from dataset |

Please refer to swagger docs for request params and response types.
127.0.0.1:8000/docs
