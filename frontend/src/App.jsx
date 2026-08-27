import { useState } from 'react'
import { ArrowRight, CalendarDays, CheckCircle2, HeartPulse, Menu, ShieldCheck, Stethoscope, X } from 'lucide-react'
import './App.css'

function App() {
  const [modal, setModal] = useState(null)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [form, setForm] = useState({ first_name: '', last_name: '', username: '', password: '' })
  const [message, setMessage] = useState('')
  const updateForm = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  const submit = async (event) => {
    event.preventDefault()
    setMessage('')
    const endpoint = modal === 'account' ? '/api/auth/account/' : '/api/auth/staff-login/'
    const body = modal === 'account' ? form : { username: form.username, password: form.password }
    try {
      const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Please check your details and try again.')
      localStorage.setItem('oniru-auth', JSON.stringify(data))
      setMessage(`Welcome, ${data.user.name || 'there'}. Your account is ready.`)
    } catch (error) { setMessage(error.message) }
  }
  return (
    <main>
      <nav className="nav shell">
        <a className="brand" href="#top" aria-label="Oniru Primary Health Centre home"><span className="brand-mark"><HeartPulse size={21} /></span><span>Oniru <strong>PHC</strong></span></a>
        <button className="menu-button" type="button" onClick={() => setMobileMenu(!mobileMenu)} aria-label="Toggle navigation">{mobileMenu ? <X size={22} /> : <Menu size={22} />}</button>
        <div className={`nav-links ${mobileMenu ? 'open' : ''}`}><a href="#services">Our services</a><a href="#about">About the centre</a><button className="text-button" type="button" onClick={() => setModal('staff')}>Staff sign in <ArrowRight size={16} /></button></div>
      </nav>
      <section className="hero shell" id="top">
        <div className="hero-copy"><p className="eyebrow"><span className="live-dot" /> Care close to home</p><h1>Good health starts with <em>being heard.</em></h1><p className="hero-lede">Friendly, dependable primary care for Oniru and the communities around Victoria Island, Lagos.</p><div className="hero-actions"><button className="button button-primary" type="button" onClick={() => setModal('account')}>Create a patient account <ArrowRight size={18} /></button><button className="button button-quiet" type="button" onClick={() => setModal('staff')}>Staff sign in</button></div><div className="trust-line"><ShieldCheck size={17} /> Your care, handled with privacy and respect.</div></div>
        <div className="hero-art" aria-label="A welcoming consultation room at Oniru Primary Health Centre"><div className="sun-disc" /><div className="art-card art-card-main"><div className="cross">+</div><span>Oniru<br /><b>Primary Health Centre</b></span></div><div className="art-card art-card-note"><CheckCircle2 size={18} /><span>Here when<br />you need us</span></div><div className="plant"><span /><span /><span /><span /></div><div className="window"><i /><i /><i /></div></div>
      </section>
      <section className="intro-band" id="about"><div className="shell intro-grid"><p className="section-tag">A better first step</p><h2>Healthcare that feels <em>human.</em></h2><p>From everyday check-ups to maternal care and health education, our team is here to make your next step feel clear.</p></div></section>
      <section className="services shell" id="services"><div className="section-heading"><div><p className="section-tag">What we offer</p><h2>Care for every chapter.</h2></div><a href="#top">View all services <ArrowRight size={16} /></a></div><div className="service-grid"><article><span className="service-icon teal"><Stethoscope size={22} /></span><h3>General consultations</h3><p>Thoughtful care for everyday health needs, from check-ups to ongoing support.</p></article><article><span className="service-icon coral"><HeartPulse size={22} /></span><h3>Maternal & child health</h3><p>Compassionate guidance for mothers, babies, and growing families.</p></article><article><span className="service-icon mustard"><CalendarDays size={22} /></span><h3>Appointments made easy</h3><p>Create an account to request care and keep your health journey organized.</p></article></div></section>
      <footer className="footer"><div className="shell footer-inner"><span>Oniru PHC</span><span>Oniru, Victoria Island, Lagos</span><span>Open Monday - Saturday · 8:00 - 18:00</span></div></footer>
      {modal && <div className="modal-backdrop" onMouseDown={() => setModal(null)}><section className="modal" onMouseDown={(event) => event.stopPropagation()}><button className="close-button" type="button" onClick={() => setModal(null)} aria-label="Close"><X size={20} /></button><p className="section-tag">{modal === 'account' ? 'Patient access' : 'Team access'}</p><h2>{modal === 'account' ? 'Create your account.' : 'Welcome back, team.'}</h2><p className="modal-copy">{modal === 'account' ? 'Keep your appointments and care details in one place.' : 'Sign in to your secure staff workspace.'}</p><form onSubmit={submit}>{modal === 'account' && <div className="form-row"><label>First name<input name="first_name" required value={form.first_name} onChange={updateForm} /></label><label>Last name<input name="last_name" value={form.last_name} onChange={updateForm} /></label></div>}<label>Username<input name="username" required value={form.username} onChange={updateForm} /></label><label>Password<input name="password" type="password" required minLength="8" value={form.password} onChange={updateForm} /></label><button className="button button-primary full-width" type="submit">{modal === 'account' ? 'Create account' : 'Sign in'} <ArrowRight size={18} /></button></form>{message && <p className="form-message">{message}</p>}</section></div>}
    </main>
  )
}

export default App
