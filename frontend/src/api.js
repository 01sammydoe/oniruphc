const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function apiRequest(path, options = {}) {
  const auth = JSON.parse(localStorage.getItem('oniru-auth') || 'null')
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(auth?.token ? { Authorization: `Token ${auth.token}` } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw new Error('The clinic service is unavailable. Please try again.')
  }

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    if (response.status === 409 && path === '/auth/account/') {
      throw new Error('That username already has an account. Please choose a different username or sign in.')
    }
    throw new Error(data.detail || 'Something went wrong. Please try again.')
  }
  return data
}

export function createPatientAccount(details) {
  return apiRequest('/auth/account/', {
    method: 'POST',
    body: JSON.stringify(details),
  })
}

export function loginStaff(details) {
  return apiRequest('/auth/staff-login/', {
    method: 'POST',
    body: JSON.stringify(details),
  })
}

export function loginPatient(details) {
  return apiRequest('/auth/patient-login/', {
    method: 'POST',
    body: JSON.stringify(details),
  })
}

export function getAppointments() {
  return apiRequest('/appointments/')
}

export function bookAppointment(details) {
  return apiRequest('/appointments/', {
    method: 'POST',
    body: JSON.stringify(details),
  })
}

export function getMyAppointments() {
  return apiRequest('/appointments/mine/')
}

export function deleteMyAppointment(appointmentId) {
  return apiRequest(`/appointments/mine/${appointmentId}/`, { method: 'DELETE' })
}

export function lookupFrontDeskPatient(patientNumber) {
  return apiRequest(`/frontdesk/patient/?patient_number=${encodeURIComponent(patientNumber)}`)
}

export function recordFrontDeskPayment(appointmentId) {
  return apiRequest(`/frontdesk/appointments/${appointmentId}/pay/`, { method: 'POST' })
}

export function getFrontDeskRevenue(date) {
  return apiRequest(`/frontdesk/revenue/?date=${encodeURIComponent(date)}`)
}

export function getPatientProfile() {
  return apiRequest('/profile/')
}

export function lookupNurseVitals(patientNumber) {
  return apiRequest(`/nurse/patient-vitals/?patient_number=${encodeURIComponent(patientNumber)}`)
}

export function saveNurseVitals(details) {
  return apiRequest('/nurse/patient-vitals/', {
    method: 'POST',
    body: JSON.stringify(details),
  })
}

export function lookupDoctorPatient(patientNumber) {
  return apiRequest(`/doctor/patient-record/?patient_number=${encodeURIComponent(patientNumber)}`)
}

export function saveDoctorConsultation(details) {
  return apiRequest('/doctor/patient-record/', {
    method: 'POST',
    body: JSON.stringify(details),
  })
}

export function getDoctorSummary(date) {
  return apiRequest(`/doctor/summary/?date=${encodeURIComponent(date)}`)
}
