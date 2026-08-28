import { useEffect, useState } from 'react'
import { ArrowRight, CalendarDays, CheckCircle2, HeartPulse, Menu, Printer, Search, ShieldCheck, Stethoscope, UserRound, X } from 'lucide-react'
import { bookAppointment, createPatientAccount, deleteMyAppointment, getAppointments, getFrontDeskRevenue, getMyAppointments, loginPatient, loginStaff, lookupFrontDeskPatient, recordFrontDeskPayment } from './api'
import './App.css'

const initialForm = {
  first_name: '', middle_name: '', last_name: '', state_of_origin: '', nationality: 'Nigerian',
  email: '', phone: '', blood_group: '', next_of_kin: '', date_of_birth: '', address: '',
  username: '', password: '',
}

const initialAppointment = { full_name: '', email: '', phone: '', service: 'General consultation', appointment_date: '', appointment_time: '', notes: '' }

const appointmentServices = ['General consultation', 'Antenatal care', 'Immunization (0-5 years)', 'Family planning', 'Lab/test result']

const profileFields = [
  ['surname', 'Surname'], ['middle_name', 'Middle name'], ['first_name', 'First name'],
  ['state_of_origin', 'State of origin'], ['nationality', 'Nationality'], ['email', 'Email'],
  ['phone', 'Phone'], ['blood_group', 'Blood group'], ['next_of_kin', 'Next of kin'],
  ['date_of_birth', 'Date of birth'], ['address', 'Address'],
]

function countdownTo(date, time) {
  const remaining = new Date(`${date}T${time}`).getTime() - Date.now()
  if (remaining <= 0) return 'Due now'
  const days = Math.floor(remaining / 86400000)
  const hours = Math.floor((remaining % 86400000) / 3600000)
  const minutes = Math.floor((remaining % 3600000) / 60000)
  return `${days}d ${hours}h ${minutes}m`
}

const naira = (amount) => `₦${Number(amount).toLocaleString('en-NG')}`

function FrontDeskPage({ auth, onSignOut }) {
  const today = new Date().toISOString().slice(0, 10)
  const [patientNumber, setPatientNumber] = useState('')
  const [patientResult, setPatientResult] = useState(null)
  const [lookupMessage, setLookupMessage] = useState('')
  const [revenue, setRevenue] = useState({ total: '0', by_service: [] })
  const [revenueDate, setRevenueDate] = useState(today)
  const [loading, setLoading] = useState(false)
  const loadRevenue = (date) => getFrontDeskRevenue(date).then(setRevenue).catch((error) => setLookupMessage(error.message))
  useEffect(() => { loadRevenue(revenueDate) }, [revenueDate])
  const lookup = async (event) => {
    event.preventDefault(); setLoading(true); setLookupMessage(''); setPatientResult(null)
    try { setPatientResult(await lookupFrontDeskPatient(patientNumber)) } catch (error) { setLookupMessage(error.message) } finally { setLoading(false) }
  }
  const markPaid = async (appointmentId) => {
    try { await recordFrontDeskPayment(appointmentId); setLookupMessage('Payment recorded successfully.'); setPatientResult(await lookupFrontDeskPatient(patientNumber)); loadRevenue(revenueDate) } catch (error) { setLookupMessage(error.message) }
  }
  const maxRevenue = Math.max(...revenue.by_service.map((item) => Number(item.total)), 1)
  return <main className="staff-page"><nav className="staff-nav shell"><div className="brand"><span className="brand-mark"><HeartPulse size={21} /></span><span>Oniru <strong>PHC</strong></span></div><div className="staff-user"><span>Front desk</span><strong>{auth.user.name}</strong><button className="text-button" type="button" onClick={onSignOut}>Sign out <ArrowRight size={16} /></button></div></nav><section className="staff-shell shell"><div className="staff-heading"><div><p className="section-tag">Front desk workspace</p><h1>Good morning, {auth.user.name.split(' ')[0]}.</h1><p>Look up appointments, record payments, and keep today moving.</p></div><div className="staff-date">{new Date().toLocaleDateString('en-NG', { weekday: 'long', day: 'numeric', month: 'long' })}</div></div><div className="staff-layout"><section className="staff-panel lookup-panel"><div className="panel-heading"><div><p className="section-tag">Patient check-in</p><h2>Find an appointment</h2></div><SearchIcon /></div><form className="lookup-form" onSubmit={lookup}><label>Patient number<input value={patientNumber} onChange={(event) => setPatientNumber(event.target.value)} placeholder="e.g. PHC-0001" required /></label><button className="button button-primary" disabled={loading} type="submit">{loading ? 'Searching...' : 'Search patient'} <ArrowRight size={17} /></button></form>{lookupMessage && <p className="staff-message">{lookupMessage}</p>}{patientResult && <div className="patient-result"><div className="patient-summary"><div><span className="result-label">Patient</span><h3>{patientResult.patient.name}</h3><p>{patientResult.patient.patient_number} · {patientResult.patient.phone}</p></div><span className="result-chip">{patientResult.appointments.length} appointment{patientResult.appointments.length === 1 ? '' : 's'}</span></div>{patientResult.appointments.length ? patientResult.appointments.map((appointment) => <div className="appointment-detail" key={appointment.id}><div><strong>{appointment.service}</strong><span>{appointment.date} at {appointment.time}</span><small>{appointment.status}</small></div><div className="appointment-price"><strong>{naira(appointment.price)}</strong>{appointment.payment_status === 'Paid' ? <span className="paid-label">Paid</span> : <button type="button" onClick={() => markPaid(appointment.id)}>Mark paid</button>}</div></div>) : <p className="empty-result">This patient has no appointments on record.</p>}</div>}</section><section className="staff-panel revenue-panel"><div className="panel-heading"><div><p className="section-tag">Revenue overview</p><h2>Daily revenue</h2></div><button className="print-button" type="button" onClick={() => window.print()} title="Print daily revenue"><PrinterIcon /></button></div><div className="revenue-controls"><label>Date<input type="date" value={revenueDate} onChange={(event) => setRevenueDate(event.target.value)} /></label></div><div className="revenue-total"><span>Total collected</span><strong>{naira(revenue.total)}</strong></div><div className="bar-chart">{revenue.by_service.length ? revenue.by_service.map((item) => <div className="bar-row" key={item.service}><span title={item.service}>{item.service}</span><div className="bar-track"><i style={{ width: `${(Number(item.total) / maxRevenue) * 100}%` }} /></div><strong>{naira(item.total)}</strong></div>) : <p className="empty-result">No paid appointments for this date.</p>}</div><p className="report-note">Print includes today&apos;s paid services and totals.</p></section></div></section></main>
}

function SearchIcon() { return <Search className="panel-icon" size={28} /> }
function PrinterIcon() { return <Printer size={19} /> }

function ProfilePage({ profile, onSignOut }) {
  const [bookingOpen, setBookingOpen] = useState(false)
  const [booking, setBooking] = useState({ full_name: `${profile.first_name} ${profile.surname}`, email: profile.email, phone: profile.phone, service: 'General consultation', appointment_date: '', appointment_time: '', notes: '' })
  const minimumDate = new Date().toISOString().slice(0, 10)
  const [bookingMessage, setBookingMessage] = useState('')
  const [bookedAppointment, setBookedAppointment] = useState(null)
  const [myAppointments, setMyAppointments] = useState([])
  const [countdown, setCountdown] = useState('')
  const activeAppointment = myAppointments.find((appointment) => ['pending', 'confirmed'].includes(appointment.status))
  useEffect(() => { getMyAppointments().then(setMyAppointments).catch(() => {}) }, [])
  useEffect(() => {
    if (!activeAppointment) return undefined
    const updateCountdown = () => setCountdown(countdownTo(activeAppointment.date, activeAppointment.time))
    updateCountdown()
    const timer = setInterval(updateCountdown, 60000)
    return () => clearInterval(timer)
  }, [activeAppointment])
  const submitBooking = async (event) => {
    event.preventDefault()
    try {
      const response = await bookAppointment(booking)
      setBookedAppointment(response.appointment)
      setBookingOpen(false)
      setBookingMessage('Your appointment request has been received.')
      getMyAppointments().then(setMyAppointments).catch(() => {})
    } catch (error) { setBookingMessage(error.message) }
  }
  const removeAppointment = async () => {
    if (!window.confirm('Delete this appointment?')) return
    try {
      await deleteMyAppointment(activeAppointment.id)
      setMyAppointments([])
      setBookingMessage('Appointment deleted. You can now book another appointment.')
    } catch (error) { setBookingMessage(error.message) }
  }
  return (
    <main className="profile-page">
      <nav className="nav shell"><a className="brand" href="#profile"><span className="brand-mark"><HeartPulse size={21} /></span><span>Oniru <strong>PHC</strong></span></a><button className="text-button" type="button" onClick={onSignOut}>Sign out <ArrowRight size={16} /></button></nav>
      <section className="profile-shell shell">
        <div className="profile-heading"><div><p className="section-tag">Patient profile</p><h1>{profile.first_name} {profile.surname}</h1><p className="profile-number">Patient number: <strong>{profile.patient_number}</strong></p></div><span className="profile-badge"><CheckCircle2 size={17} /> Account active</span></div>
        {activeAppointment ? <section className="appointment-countdown"><div><p className="section-tag">Your next appointment</p><h2>{activeAppointment.service}</h2><p>{activeAppointment.date} at {activeAppointment.time} · {activeAppointment.status_label}</p></div><strong>{countdown}</strong><button className="delete-appointment" type="button" onClick={removeAppointment}>Delete appointment</button><small>Due appointments are removed automatically. You can also delete this appointment at any time.</small></section> : <button className="button button-primary profile-book-button" type="button" onClick={() => { setBookingMessage(''); setBookingOpen(true) }}><CalendarDays size={18} /> Book an appointment</button>}
        <div className="profile-grid"><section className="profile-card"><div className="card-heading"><UserRound size={20} /><h2>Personal details</h2></div>{profileFields.slice(0, 5).map(([key, label]) => <div className="detail" key={key}><span>{label}</span><strong>{profile[key] || 'Not provided'}</strong></div>)}</section><section className="profile-card"><div className="card-heading"><HeartPulse size={20} /><h2>Contact & health</h2></div>{profileFields.slice(5).map(([key, label]) => <div className="detail" key={key}><span>{label}</span><strong>{profile[key] || 'Not provided'}</strong></div>)}</section></div>
        <div className="profile-note"><ShieldCheck size={18} /><span>Your information is kept private and used to support your care at Oniru PHC.</span></div>
        {bookedAppointment && <section className="booked-appointment"><div><p className="section-tag">Appointment booked</p><h2>Your visit is in the system.</h2><p>Reference: <strong>#{bookedAppointment.id}</strong></p></div><div className="booked-details"><span><b>Service</b>{bookedAppointment.service}</span><span><b>Date</b>{bookedAppointment.date}</span><span><b>Time</b>{bookedAppointment.time}</span><span><b>Price</b>{naira(bookedAppointment.price)}</span><span><b>Status</b>{bookedAppointment.status_label || 'Pending confirmation'}</span></div><button className="button button-quiet" type="button" onClick={() => setBookedAppointment(null)}>Close details</button></section>}
      </section>
      {bookingOpen && <div className="modal-backdrop" onMouseDown={() => setBookingOpen(false)}><section className="modal" onMouseDown={(event) => event.stopPropagation()}><button className="close-button" type="button" onClick={() => setBookingOpen(false)} aria-label="Close"><X size={20} /></button><p className="section-tag">Online booking</p><h2>Reserve your visit.</h2><p className="modal-copy">Your contact details are already filled in from your profile.</p><form onSubmit={submitBooking}><label>Service<select value={booking.service} onChange={(event) => setBooking({ ...booking, service: event.target.value })}>{appointmentServices.map((service) => <option key={service}>{service}</option>)}</select></label><div className="form-row"><label>Date<input type="date" min={minimumDate} required value={booking.appointment_date} onChange={(event) => setBooking({ ...booking, appointment_date: event.target.value })} /></label><label>Preferred time<input type="time" required value={booking.appointment_time} onChange={(event) => setBooking({ ...booking, appointment_time: event.target.value })} /></label></div><label>Notes (optional)<textarea value={booking.notes} onChange={(event) => setBooking({ ...booking, notes: event.target.value })} /></label><button className="button button-primary full-width" type="submit">Request appointment <ArrowRight size={18} /></button></form>{bookingMessage && <p className="form-message">{bookingMessage}</p>}</section></div>}
    </main>
  )
}

function App() {
  const [modal, setModal] = useState(null)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [profile, setProfile] = useState(() => JSON.parse(localStorage.getItem('oniru-profile') || 'null'))
  const [staffAuth, setStaffAuth] = useState(() => { const auth = JSON.parse(localStorage.getItem('oniru-auth') || 'null'); return auth?.user?.role === 'front_desk' ? auth : null })
  const [form, setForm] = useState(initialForm)
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [appointments, setAppointments] = useState([])
  const [appointmentForm, setAppointmentForm] = useState(initialAppointment)
  useEffect(() => { getAppointments().then(setAppointments).catch(() => {}) }, [])
  const updateForm = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  const openModal = (type) => { setMessage(''); setModal(type) }
  const submit = async (event) => {
    event.preventDefault(); setMessage(''); setIsSubmitting(true)
    try {
      const data = modal === 'appointment' ? await bookAppointment(appointmentForm) : modal === 'account'
        ? await createPatientAccount(form)
        : modal === 'patient' ? await loginPatient({ username: form.username, password: form.password })
          : await loginStaff({ username: form.username, password: form.password })
      localStorage.setItem('oniru-auth', JSON.stringify(data))
      if (modal === 'appointment') { setMessage('Your appointment request has been received.'); setAppointmentForm(initialAppointment); getAppointments().then(setAppointments).catch(() => {}) }
      else if (data.profile) { localStorage.setItem('oniru-profile', JSON.stringify(data.profile)); setProfile(data.profile); setModal(null) }
      else if (data.user.role === 'front_desk') {
        localStorage.removeItem('oniru-profile')
        setProfile(null)
        setStaffAuth(data)
        setModal(null)
      }
      else setMessage(`Welcome, ${data.user.name}. Staff access is ready.`)
    } catch (error) { setMessage(error.message) } finally { setIsSubmitting(false) }
  }
  if (staffAuth) return <FrontDeskPage auth={staffAuth} onSignOut={() => { localStorage.removeItem('oniru-auth'); setStaffAuth(null) }} />
  if (profile) return <ProfilePage profile={profile} onSignOut={() => { localStorage.removeItem('oniru-profile'); localStorage.removeItem('oniru-auth'); setProfile(null) }} />
  return (
    <main>
      <nav className="nav shell"><a className="brand" href="#top" aria-label="Oniru Primary Health Centre home"><span className="brand-mark"><HeartPulse size={21} /></span><span>Oniru <strong>PHC</strong></span></a><button className="menu-button" type="button" onClick={() => setMobileMenu(!mobileMenu)} aria-label="Toggle navigation">{mobileMenu ? <X size={22} /> : <Menu size={22} />}</button><div className={`nav-links ${mobileMenu ? 'open' : ''}`}><a href="#services">Our services</a><a href="#appointments">Appointments</a><button className="text-button patient-sign-in" type="button" onClick={() => openModal('patient')}>Sign in <ArrowRight size={16} /></button><button className="text-button" type="button" onClick={() => openModal('staff')}>Staff sign in <ArrowRight size={16} /></button></div></nav>
      <section className="hero shell" id="top"><div className="hero-copy"><p className="eyebrow"><span className="live-dot" /> Care close to home</p><h1>Good health starts with <em>being heard.</em></h1><p className="hero-lede">Friendly, dependable primary care for Oniru and the communities around Victoria Island, Lagos.</p><div className="hero-actions"><button className="button button-primary" type="button" onClick={() => openModal('account')}>Create a patient account <ArrowRight size={18} /></button><button className="button button-quiet" type="button" onClick={() => openModal('patient')}>Patient sign in</button></div><p className="existing-account">Already registered? <button type="button" onClick={() => openModal('patient')}>Sign in to your account</button></p><div className="trust-line"><ShieldCheck size={17} /> Your care, handled with privacy and respect.</div></div><div className="hero-art" aria-label="A welcoming consultation room at Oniru Primary Health Centre"><div className="sun-disc" /><div className="art-card art-card-main"><div className="cross">+</div><span>Oniru<br /><b>Primary Health Centre</b></span></div><div className="art-card art-card-note"><CheckCircle2 size={18} /><span>Here when<br />you need us</span></div><div className="plant"><span /><span /><span /><span /></div><div className="window"><i /><i /><i /></div></div></section>
      <section className="intro-band" id="about"><div className="shell intro-grid"><p className="section-tag">A better first step</p><h2>Healthcare that feels <em>human.</em></h2><p>From everyday check-ups to maternal care and health education, our team is here to make your next step feel clear.</p></div></section>
      <section className="services shell" id="services"><div className="section-heading"><div><p className="section-tag">What we offer</p><h2>Care for every chapter.</h2></div></div><div className="service-grid"><article><span className="service-icon teal"><Stethoscope size={22} /></span><h3>General consultations</h3><p>Thoughtful care for everyday health needs, from check-ups to ongoing support.</p></article><article><span className="service-icon coral"><HeartPulse size={22} /></span><h3>Maternal & child health</h3><p>Compassionate guidance for mothers, babies, and growing families.</p></article><article><span className="service-icon mustard"><CalendarDays size={22} /></span><h3>Appointments made easy</h3><p>Create an account to request care and keep your health journey organized.</p></article></div></section>
      <section className="appointments shell" id="appointments"><div className="section-heading"><div><p className="section-tag">Plan your visit</p><h2>Book an appointment.</h2></div><button className="button button-primary" type="button" onClick={() => openModal('patient')}>Sign in to book <ArrowRight size={17} /></button></div><div className="appointment-board"><div><p className="board-label">Upcoming availability</p>{appointments.length ? appointments.map((appointment) => <div className="appointment-row" key={`${appointment.date}-${appointment.time}-${appointment.service}`}><strong>{appointment.service}</strong><span>{appointment.date} · {appointment.time}</span><small>{appointment.status}</small></div>) : <p className="empty-board">No upcoming appointments yet.</p>}</div><p className="board-note"><ShieldCheck size={17} /> Sign in to your patient profile to request an appointment. Personal details stay private.</p></div></section>
      <footer className="footer"><div className="shell footer-inner"><span>Oniru PHC</span><span>Oniru, Victoria Island, Lagos</span><span>Open Monday - Saturday · 8:00 - 18:00</span></div></footer>
      {modal && <div className="modal-backdrop" onMouseDown={() => setModal(null)}><section className="modal expanded-modal" onMouseDown={(event) => event.stopPropagation()}><button className="close-button" type="button" onClick={() => setModal(null)} aria-label="Close"><X size={20} /></button><p className="section-tag">{modal === 'account' ? 'Patient access' : modal === 'patient' ? 'Existing patient' : modal === 'appointment' ? 'Online booking' : 'Team access'}</p><h2>{modal === 'account' ? 'Create your account.' : modal === 'patient' ? 'Welcome back.' : modal === 'appointment' ? 'Reserve your visit.' : 'Welcome back, team.'}</h2><p className="modal-copy">{modal === 'account' ? 'Complete your details so we can prepare your patient record.' : modal === 'patient' ? 'Sign in to view your patient profile.' : modal === 'appointment' ? 'Tell us when you would like to be seen.' : 'Sign in to your secure staff workspace.'}</p><form onSubmit={submit}>{modal === 'appointment' && <div className="form-row"><label>Full name<input name="full_name" required value={appointmentForm.full_name} onChange={(event) => setAppointmentForm({ ...appointmentForm, full_name: event.target.value })} /></label><label>Email<input name="email" type="email" required value={appointmentForm.email} onChange={(event) => setAppointmentForm({ ...appointmentForm, email: event.target.value })} /></label><label>Phone<input name="phone" required value={appointmentForm.phone} onChange={(event) => setAppointmentForm({ ...appointmentForm, phone: event.target.value })} /></label><label>Service<select name="service" value={appointmentForm.service} onChange={(event) => setAppointmentForm({ ...appointmentForm, service: event.target.value })}><option>General consultation</option><option>Maternal & child health</option><option>Health education</option><option>Follow-up visit</option></select></label><label>Date<input name="appointment_date" type="date" required value={appointmentForm.appointment_date} onChange={(event) => setAppointmentForm({ ...appointmentForm, appointment_date: event.target.value })} /></label><label>Preferred time<input name="appointment_time" type="time" required value={appointmentForm.appointment_time} onChange={(event) => setAppointmentForm({ ...appointmentForm, appointment_time: event.target.value })} /></label><label className="wide-field">Notes (optional)<textarea name="notes" value={appointmentForm.notes} onChange={(event) => setAppointmentForm({ ...appointmentForm, notes: event.target.value })} /></label></div>}{modal === 'account' && <div className="form-row"><label>Surname<input name="last_name" required value={form.last_name} onChange={updateForm} /></label><label>Middle name<input name="middle_name" value={form.middle_name} onChange={updateForm} /></label><label>First name<input name="first_name" required value={form.first_name} onChange={updateForm} /></label><label>State of origin<input name="state_of_origin" required value={form.state_of_origin} onChange={updateForm} /></label><label>Nationality<input name="nationality" required value={form.nationality} onChange={updateForm} /></label><label>Date of birth<input name="date_of_birth" type="date" required value={form.date_of_birth} onChange={updateForm} /></label><label>Email<input name="email" type="email" required value={form.email} onChange={updateForm} /></label><label>Phone<input name="phone" required value={form.phone} onChange={updateForm} /></label><label>Blood group<input name="blood_group" placeholder="e.g. O+" value={form.blood_group} onChange={updateForm} /></label><label>Next of kin<input name="next_of_kin" required value={form.next_of_kin} onChange={updateForm} /></label><label className="wide-field">Address<textarea name="address" required value={form.address} onChange={updateForm} /></label></div>}{modal !== 'appointment' && <div className="account-credentials"><label>Username<input name="username" placeholder="e.g. amaka.obi" required value={form.username} onChange={updateForm} /></label><label>Password<input name="password" type="password" required minLength="8" value={form.password} onChange={updateForm} /></label></div>}<button className="button button-primary full-width" disabled={isSubmitting} type="submit">{isSubmitting ? 'Connecting...' : modal === 'account' ? 'Create account' : modal === 'appointment' ? 'Request appointment' : 'Sign in'} {!isSubmitting && <ArrowRight size={18} />}</button></form>{message && <p className="form-message">{message}</p>}</section></div>}
    </main>
  )
}

export default App
