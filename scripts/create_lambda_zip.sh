## Move back
cd ...

## Remove old zip
rm lambda_whichbins.zip

## Pip install from requirements.txt 
pip install --target ./package -r requirements.txt 

## Move intp package
cd package

## Zip everything into a nice zip file
zip -r ../lambda_whichbins.zip .

## Move back
cd ..

## Zip in main.py and waste_collection.py
zip lambda_whichbins.zip main.py waste_collection.py
