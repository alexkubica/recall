import {readFile,writeFile,mkdir,copyFile,rm} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const manifest=JSON.parse(await readFile(path.join(root,'public/offline-assets.json'),'utf8'));
const out=path.join(root,'dist');
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
for(const name of [...manifest.assets.filter(x=>x!=='./').map(x=>x.slice(2)),'sw.js','offline-assets.json']){
 if(name.startsWith('/')||name.split('/').includes('..'))throw Error('Unsafe asset '+name);
 const dest=path.join(out,name);await mkdir(path.dirname(dest),{recursive:true});await copyFile(path.join(root,'public',name),dest);
}
await writeFile(path.join(out,'.nojekyll'),'');
console.log(`Packaged ${manifest.assets.length+2} runtime files in dist/`);
