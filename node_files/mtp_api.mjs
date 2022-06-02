/*
Server-side code to process MJML to HTML conversion requests.
It processes a given file name, which should have been previously sent to the server, converts it to MJML then sends it
back to the requester.
 */
import * as http from 'http'
import mjml2html from 'mjml'
import * as fs from 'fs'

const hostname = '127.0.0.1'
const port = 3000;

const fileName = 'test_mjml.mjml';

const fileObject = fs.readFileSync(fileName, 'utf8')

var htmlOutput = mjml2html(fileObject.toString());
console.log(htmlOutput)

var server = http.createServer(function (req, res) {
    res.writeHead(200, {
        'Content-Type': 'text/plain'
    });
    res.end(htmlOutput.html);
});
server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});

