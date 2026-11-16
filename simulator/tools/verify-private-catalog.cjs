/* Explicit opt-in; reads a private sample and emits only reviewed metadata. */
const fs=require('node:fs');const crypto=require('node:crypto');const assert=require('node:assert/strict');
const catalog=require(process.argv.includes('--navigation')?'../navigation-catalog.js':'../catalog.js');
if(!process.argv[2]) {console.error('Usage: node tools/verify-private-catalog.cjs PATH_TO_PRIVATE_V14 [--navigation]');process.exitCode=2;}
else {
  try {
    const data=fs.readFileSync(process.argv[2]), hash=buffer=>crypto.createHash('sha256').update(buffer).digest('hex');
    assert.equal(hash(data),catalog.fingerprint,'Different V1.4 fingerprint; catalog not verified');
    let count=0;
    for(const entry of catalog.entries) for(const offset of entry.occurrences) {
      const expected=Buffer.from(entry.en+'\0','ascii');
      assert.ok(data.subarray(offset,offset+expected.length).equals(expected),'Known catalog mismatch at '+offset);count++;
    }
    assert.equal(hash(fs.readFileSync(process.argv[2])),hash(data),'Input changed');
    console.log(JSON.stringify({sha256:hash(data),knownLabels:catalog.entries.filter(e=>e.occurrences.length).length,matchedNulOccurrences:count,inputUnchanged:true},null,2));
  } catch(error) {console.error(error.message);process.exitCode=1;}
}
