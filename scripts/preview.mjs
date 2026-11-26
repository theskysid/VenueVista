// A dependency-free server for previewing the built Angular application.
// Usage: PREVIEW_API_PORT=8090 node scripts/preview.mjs (default UI port 4300).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../frontend/dist/venuevista/browser');
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png'};
http.createServer((req,res)=>{
  if(req.url.startsWith('/api/')||req.url.startsWith('/actuator/')){
    const proxy=http.request({hostname:'127.0.0.1',port:process.env.PREVIEW_API_PORT||8080,path:req.url,method:req.method,headers:req.headers},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res);});
    proxy.on('error',()=>{res.writeHead(502);res.end('API unavailable');});req.pipe(proxy);return;
  }
  const url=new URL(req.url,'http://localhost');let file=path.join(root,decodeURIComponent(url.pathname));
  if(!file.startsWith(root+path.sep)&&file!==root){res.writeHead(403);res.end();return;}
  if(!fs.existsSync(file)||fs.statSync(file).isDirectory())file=path.join(root,'index.html');
  res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);
}).listen(Number(process.env.PREVIEW_PORT||4300),'127.0.0.1',()=>console.log(`VenueVista preview: http://localhost:${process.env.PREVIEW_PORT||4300}`));
