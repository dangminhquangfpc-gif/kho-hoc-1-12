import { redirect } from 'next/navigation';
import { login, loggedIn } from '../../lib/auth';
export default async function Login({ searchParams }: {searchParams:Promise<{error?:string}>}) {
  if (await loggedIn()) redirect('/');
  const {error}=await searchParams;
  async function submit(form:FormData) { 'use server'; const ok=await login(String(form.get('password')||'')); redirect(ok?'/':'/login?error=1'); }
  return <main className="login"><p className="eyebrow">KHO HỌC 1–12</p><h1>Quản trị nội dung</h1><p>Chế độ phát triển cục bộ. Nhập token đã cấu hình ở server; token không được nhúng trong mã frontend.</p>{error&&<p role="alert" className="error">Thông tin đăng nhập không hợp lệ.</p>}<form action={submit}><label>Token quản trị<input name="password" type="password" required autoComplete="current-password"/></label><button>Đăng nhập</button></form></main>;
}
