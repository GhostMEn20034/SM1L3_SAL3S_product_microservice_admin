# SMILE SALES Product Microservice (Private API)

This microservice is designed for product listing and management. <br>
It provides features to manage categories, facets (Product attributes), 
variation themes (Allows to determine what's the difference between two product-siblings),
products, search terms, events, deals (Technically, it's predefined set of filters). <br>

# Setup
### 1. Clone repository with:
```bash
git clone https://github.com/GhostMEn20034/SM1L3_SAL3S_product_microservice_admin.git
```
### 2. Go to directory with project
### 3. Create .env file:
on Windows (PowerShell), run:
```powershell
New-Item -Path ".env" -ItemType "File"
```
on Unix or MacOS, run:
```bash
touch .env
```
### 4. Open any editor and paste your env variables:
```shell
MONGODB_URL=YourMongoDbURL
AWS_ACCESS_KEY_ID=fdfldfd4121331231_test # Create AWS access token and Secret access key so you can have access to the s3 bucket 
AWS_SECRET_ACCESS_KEY=fdfdfsf_re_test # Create AWS access token and Secret access key so you can have access to the s3 bucket
S3_BUCKET_NAME=your-bucket-name # S3 Bucket Name
BUCKET_BASE_URL=https://your-bucket-name.s3.region.amazonaws.com
CDN_HOST_NAME=https://some_letters.cloudfront.net # Your CloudFront distribution host name (It should provide images from your s3 bucket)
ATLAS_SEARCH_INDEX_NAME_PRODUCTS=some_index_name # The name of the search index for product search in your MongoDB cluster
ATLAS_SEARCH_INDEX_NAME_SEARCH_TERMS=search_terms_index # The name of the search index for search terms autocomplete in your MongoDB cluster
CELERY_BROKER_URL=yourBrokerURL
CELERY_RESULT_BACKEND=yourBrokerURL
EVENT_CHECK_INTERVAL_MINUTES=1 # How often Celery workers must check for events to apply discounts?
AMPQ_CONNECTION_URL=yourMessageBrokerURL
PRODUCT_CRUD_EXCHANGE_TOPIC_NAME=product_replication # Just copy that
ORDER_PROCESSING_EXCHANGE_TOPIC_NAME=order_processing_replication # just copy that
JWT_SIGNING_KEY=django-insecure-^@py4_6vvea64q!eowg8^f3d7)u71qm+l+h#wfrwylx1#$k9-@ # JWT TOKENS SIGNING KEYS (Not working right now)
USER_MICROSERVICE_BASE_URL=http://172.25.64.1:8000 # Base url of the user microservice (You can just leave it, because functionality related to this value is not working)
USER_MICROSERVICE_KEY=Lf43434243 # just leave it, because functionality related to this value is not working
VERIFY_USERS_REQUESTS=0 # just leave it
ALLOWED_ORIGINS=http://localhost:3001 # Your CORS Allowed Origins
```

### 5. Insert facet types into MongoDB cluster:
```shell
[{
  "_id": {
    "$oid": "64dbb95b8eb99a0fa0bb4090"
  },
  "name": "String",
  "value": "string"
},
{
  "_id": {
    "$oid": "64dbb9a18eb99a0fa0bb4091"
  },
  "name": "Decimal",
  "value": "decimal"
},
{
  "_id": {
    "$oid": "64dbba578eb99a0fa0bb4093"
  },
  "name": "List",
  "value": "list"
},
{
  "_id": {
    "$oid": "64dbbab58eb99a0fa0bb4094"
  },
  "name": "Bivariate",
  "value": "bivariate"
},
{
  "_id": {
    "$oid": "64dfa72b2788641292311abd"
  },
  "name": "Integer",
  "value": "integer"
},
{
  "_id": {
    "$oid": "651081e68a9f3c3e2f89862e"
  },
  "name": "Trivariate",
  "value": "trivariate"
}]
```


# Running the app
### 1. Enter the command below:
```shell
docker compose up -d
```
### 2. To shut down the app, enter the command below:
```shell
docker compose down
```