import { loggedIn, api } from '../../../lib/auth';
export async function GET() {
  if (!await loggedIn()) return Response.json({error:'Unauthorized'},{status:401});
  const rows=await api('/admin/questions');
  return new Response(JSON.stringify({questions:rows.map((r:{question:unknown})=>r.question)},null,2),{headers:{'Content-Type':'application/json; charset=utf-8','Content-Disposition':'attachment; filename="questions.json"','Cache-Control':'no-store'}});
}
