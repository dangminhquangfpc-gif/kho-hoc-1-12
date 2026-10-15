import { cookies } from 'next/headers';
import { createHmac, randomBytes, timingSafeEqual } from 'node:crypto';
import { redirect } from 'next/navigation';

const name = 'khohoc_admin';
function key() {
  const token = process.env.KHOHOC_ADMIN_TOKEN;
  if (!token || token.length < 24) throw new Error('Cần cấu hình token quản trị cục bộ ≥ 24 ký tự.');
  if (process.env.KHOHOC_MODE === 'production') throw new Error('Supabase Auth production chưa triển khai.');
  return token;
}
function signature(payload: string) { return createHmac('sha256', key()).update(payload).digest('hex'); }
export function equal(a: string, b: string) { const x=Buffer.from(a), y=Buffer.from(b); return x.length===y.length && timingSafeEqual(x,y); }
export async function loggedIn() {
  const cookie = (await cookies()).get(name)?.value;
  if (!cookie) return false;
  const [expiry, nonce, sig] = cookie.split('.');
  if (!expiry || !nonce || !sig || Number(expiry) < Date.now()) return false;
  return equal(sig, signature(expiry+'.'+nonce));
}
export async function requireAdmin() { if (!await loggedIn()) redirect('/login'); }
export async function login(password: string) {
  if (!equal(password, key())) return false;
  const payload = `${Date.now()+3600000}.${randomBytes(16).toString('hex')}`;
  (await cookies()).set(name,payload+'.'+signature(payload),{httpOnly:true,sameSite:'strict',secure:process.env.NODE_ENV==='production',path:'/',maxAge:3600});
  return true;
}
export async function logout() { (await cookies()).delete(name); }
export async function api(path: string, init: RequestInit = {}) {
  await requireAdmin();
  const response = await fetch((process.env.API_BASE_URL || 'http://127.0.0.1:8000')+path,{...init,cache:'no-store',headers:{'Content-Type':'application/json',Authorization:'Bearer '+key(),...init.headers}});
  if (!response.ok) { const body=await response.json().catch(()=>({detail:'API không khả dụng'})); throw new Error(typeof body.detail==='string'?body.detail:JSON.stringify(body.detail)); }
  return response.json();
}
