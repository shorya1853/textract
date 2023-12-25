docker run -it -d -p 9000:8080 \
   -v ./:/var/task \
   -e AWS_ACCESS_KEY_ID=AKIA5AFK32U74MDCVJKR \
   -e AWS_SECRET_ACCESS_KEY=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 \
   temp

curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d @/home/shorya-dubey/Documents/Folder/test/resolving/tesseract-app/event.json

tesseract  --tessdata-dir $TESSDATA_PREFIX ./filled_form.png stdout --oem 2 -l eng