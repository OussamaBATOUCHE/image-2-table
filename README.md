# Scan 2 Digital Version

## Background
This software is ment to be used served as an API endpoint. The main idea is to transform a scanned document into a digital version. The scanned documents came in pdf or (jpg, jpeg) formats, and include text as Titles, paragraphs, dates, tables, etc. The content is in Arabic or in French, but the API will always return a French output. 

## How to Use
<ol>
Once logged in into the server:
 <li>
    ```sh
    cd ../prjcts
 </li>

 <li>
    ```sh
    source s2dv/bin/activate
 </li>

 <li>
    ```sh
    cd image-2-table
 </li>

 <li>
    ```sh
    cd python3 app.py
 </li>
</ol>

Now you can POST call the API via : ```sh http://localhost:5001/api/s2dv and include the following variables:
<ul>
<li>```sh scan_id``` :  This is the unique ID (string) for the scanned document, it will be included in the response in a JSON format.</li>
<li>```sh scan_file</li>
</ul>
`git clone https://github.com/username/repo.git`

As a response, you will receive a JSON in the following architecture:
```json
   {

   }
    