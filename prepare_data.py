"""Convert normalized local CSVs into the static dashboard's JSON. No network access."""
from pathlib import Path
import argparse,csv,json
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--products',type=Path,default=root/'dist/example_products.csv')
parser.add_argument('--feedback',type=Path,default=root/'dist/example_feedback.csv')
parser.add_argument('--date',default='합성 예제 · 2026-10-29')
parser.add_argument('--output',type=Path,default=root/'dist/data.json')
args=parser.parse_args()
def read(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
products=read(args.products);feedback=read(args.feedback)
for p in products:
 for field in ['id','platform','brand','name','category','price']:
  if not p.get(field):raise ValueError(f'Missing product {field}')
 p['price']=int(p['price']);p['discount']=int(p['discount']) if p.get('discount') else None
ids=[p['id'] for p in products]
if len(ids)!=len(set(ids)):raise ValueError('Duplicate product IDs')
seen=set()
for r in feedback:
 if r['product'] not in ids:raise ValueError('Unmatched feedback product ID')
 key=(r['product'],r['type'],r['id'])
 if key in seen:raise ValueError('Duplicate feedback record')
 seen.add(key)
 r['rating']=int(float(r['rating'])) if r.get('rating') else None
 if r['type']=='리뷰' and r['rating'] not in range(1,6):raise ValueError('Invalid review rating')
 r['total']=int(r['total']);r['tags']=json.loads(r['tags'])
 if not isinstance(r['tags'],list):raise ValueError('Tags must be a JSON array')
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps({'products':products,'feedback':feedback,'date':args.date},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Generated {len(products)} products and {len(feedback)} feedback records')
