# Scan 2 Digital Version

## Background
This software is ment to be used served as an API endpoint. The main idea is to transform a scanned document into a digital version. The scanned documents came in pdf or (jpg, jpeg) formats, and include text as Titles, paragraphs, dates, tables, etc. The content is in Arabic or in French, but the API will always return a French output. 

## How to Use
Once logged in into the server, follow these steps:

```sh
   > cd ../prjcts
   > source s2dv/bin/activate
   > cd image-2-table
   > python3 app.py
```

To test if the API works, you can GET request ```http://localhost:5001/```.

Now you can POST call the API via ```http://localhost:5001/api/s2dv``` and include the following variables:

- ```scan_id``` :  This is the unique ID (string) for the scanned document, it will be included in the response in a JSON format.
- ```scan_file```: your scanned file in pdf, jpg, or jpeg.
- ```tkn```: your request token.


As a response, you will receive a JSON in the following architecture:
```json
   {
      "html_content": "<html><body><h1>Title here</h1><p>paragraph here</p></body></html>",
      "savedat": "./file/data_here",
      "scan_id": "scan_id_x",
      "sector": "Pharma",
      "title": "your title here"
   }
```

If you want to retrieve previous digital version, you can POST call the API via ```http://localhost:5001/api/retrieve``` and include the following variables:

- ```savedat```: the same as returned in the repose JSON file.
- ```tkn```: your request token.

And Voila!

_______________________
Dev By <a href="https://github.com/OussamaBATOUCHE">OussamaBatouche</a>