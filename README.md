what i do...

## To run in Lambda:

1. Create Lambda Function using Python 3.12, x86_64, timeout of 30secs or more and Handler as main.handler
2. Upload lambda_whichbins.zip to Lambda Function
3. Add environment variables to Lambda (from your .env file, using .env.example as example)
4. Schedule your Lambda to run the DAY BEFORE your bins are due

## To run 'locally':

docker compose up -d --build which_bins --no-cache
