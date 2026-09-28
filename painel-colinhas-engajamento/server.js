const http=require('http');
const fs=require('fs');
const path=require('path');

const root=__dirname;
const port=Number(process.env.PORT||3000);

function type(p){
  if(p.endsWith('.html')) return 'text/html; charset=utf-8';
  if(p.endsWith('.css')) return 'text/css; charset=utf-8';
  if(p.endsWith('.js')) return 'application/javascript; charset=utf-8';
  if(p.endsWith('.json')) return 'application/json; charset=utf-8';
  return 'application/octet-stream';
}

http.createServer((req,res)=>{
  let pathname;
  try{pathname=decodeURIComponent(new URL(req.url,'http://local').pathname)}catch{pathname='/'}
  if(pathname==='/'||pathname==='') pathname='/index.html';
  const file=path.join(root,pathname.replace(/^\/+/, ''));
  if(!file.startsWith(root)){res.writeHead(403);res.end('Forbidden');return}
  fs.readFile(file,(err,data)=>{
    if(err){
      fs.readFile(path.join(root,'index.html'),(e,fallback)=>{
        if(e){res.writeHead(404);res.end('Not found');return}
        res.writeHead(200,{'content-type':'text/html; charset=utf-8','cache-control':'no-store'});
        res.end(fallback);
      });
      return;
    }
    res.writeHead(200,{'content-type':type(file),'cache-control':'no-store'});
    res.end(data);
  });
}).listen(port,'0.0.0.0',()=>console.log('Listening on '+port));
