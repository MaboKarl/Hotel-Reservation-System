            details: document.getElementById('newRoomDetails').value
            details: document.getElementById('editRoomDetails').value
// ============================================
// MAIN APPLICATION - COMPLETE FIXED VERSION
// ============================================

// ============================================
// UI HELPERS
// ============================================
function formatPeso(amount) {
    return new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP'
    }).format(Number(amount) || 0);
}

const ROOM_DETAILS = {
    STANDARD: {
        capacity: 2,
        price: 4500,
        perks: 'Wi-Fi, breakfast, city view',
        names: ['The Cozy Nook', 'The Snooze Suite']
    },
    DELUXE: {
        capacity: 4,
        price: 7000,
        perks: 'Wi-Fi, breakfast, balcony, minibar',
        names: ['The Balcony Buzz', 'The Velvet View']
    },
    SUITE: {
        capacity: 6,
        price: 12000,
        perks: 'Wi-Fi, breakfast, living room, minibar',
        names: ['The Sofa Safari', 'The Grand Hideaway']
    },
    PENTHOUSE: {
        capacity: 8,
        price: 20000,
        perks: 'Wi-Fi, breakfast, private terrace, lounge access',
        names: ['The Sky Castle', 'The Cloud Nine Loft']
    }
};
const ROOM_AVAILABILITY = {};
let bookingPage = 1;
const bookingPageSize = 5;

function getRoomDetails(room) {
    const type = room.room_type || 'STANDARD';
    const details = ROOM_DETAILS[type] || ROOM_DETAILS.STANDARD;
    const nameIndex = Number(room.room_number || room.room_id || 0) % details.names.length;
    return { ...details, type, name: details.names[nameIndex] };
}

function showMessage(text, type = 'success') {
    const container = document.querySelector('.container');
    if (!container) return;
    
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.textContent = text;
    container.prepend(msg);
    setTimeout(() => msg.remove(), 5000);
}

function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<tr><td colspan="10" style="text-align: center;">${message}</td></tr>`;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// BOOK ROOM - Quick Action
// ============================================
function bookRoom() {
    // Switch to rooms tab
    const roomsTab = document.querySelector('[data-tab="rooms"]');
    if (roomsTab) roomsTab.click();
    showMessage('Select a room to book', 'info');
}

// ============================================
// SHOW/HIDE ADMIN TABS
// ============================================
function setupRoleBasedUI() {
    const isAdminUser = isAdmin ? isAdmin() : false;

    const bookingsTabLabel = document.getElementById('bookingsTabLabel');
    const bookingsHeading = document.getElementById('bookingsHeading');
    if (isAdminUser) {
        if (bookingsTabLabel) bookingsTabLabel.textContent = 'Booked Rooms';
        if (bookingsHeading) bookingsHeading.textContent = 'Booked Rooms';
    }
    
    document.querySelectorAll('.admin-only').forEach(el => {
        if (isAdminUser) {
            el.style.display = '';
        } else {
            el.style.display = 'none';
        }
    });
}

// ============================================
// LOAD DASHBOARD
// ============================================
async function loadDashboard() {
    try {
        // Load occupancy
        const occResponse = await apiRequest('/reports/occupancy');
        const occData = await occResponse.json();
        const occupancy = occData.data || occData;
        
        const totalRooms = document.getElementById('totalRooms');
        const bookedRooms = document.getElementById('bookedRooms');
        const availableRooms = document.getElementById('availableRooms');
        const occupancyRate = document.getElementById('occupancyRate');
        const myBookings = document.getElementById('myBookings');
        const bookedCapacity = document.getElementById('bookedCapacity');
        
        if (totalRooms) totalRooms.textContent = occupancy.total_rooms || 0;
        if (bookedRooms) bookedRooms.textContent = occupancy.booked_rooms || 0;
        if (availableRooms) availableRooms.textContent = occupancy.available_rooms || 0;
        if (occupancyRate) occupancyRate.textContent = (occupancy.occupancy_rate || 0) + '%';
        
        // Load current check-ins
        const checkinsResponse = await apiRequest('/bookings/current');
        const checkinsData = await checkinsResponse.json();
        const checkins = checkinsData.data || checkinsData;

        // Count all reservations for the signed-in guest, not only checked-in stays.
        const user = getUser();
        const bookingsEndpoint = user && user.guest_id
            ? `/bookings/guest/${user.guest_id}`
            : '/bookings';
        const bookingsResponse = await apiRequest(bookingsEndpoint);
        const bookingsData = await bookingsResponse.json();
        const bookingRecords = bookingsData.data || bookingsData;
        const bookingCount = Array.isArray(bookingRecords)
            ? bookingRecords.length
            : Object.keys(bookingRecords || {}).length;

        if (myBookings) {
            myBookings.textContent = bookingCount;
        }
        if (bookedCapacity) {
            bookedCapacity.textContent = occupancy.booked_room_capacity || 0;
        }
        
        const checkinsDiv = document.getElementById('currentCheckins');
        if (checkinsDiv) {
            checkinsDiv.innerHTML = '';
            if (Array.isArray(checkins) && checkins.length > 0) {
                checkins.forEach(booking => {
                    checkinsDiv.innerHTML += `
                        <div class="stat-card">
                            <h3>Room ${booking.room_number || booking.roomNumber || 'N/A'}</h3>
                            <p>${booking.guest_name || booking.guestName || 'Guest'}</p>
                            <p>Check-out: ${booking.check_out || booking.checkOut || 'N/A'}</p>
                        </div>
                    `;
                });
            } else {
                checkinsDiv.innerHTML = '<p>No active bookings</p>';
            }
        }
        
        // Admin-only stats
        if (window.isAdmin && isAdmin()) {
            const guestsResponse = await apiRequest('/guests');
            const guestsData = await guestsResponse.json();
            const guests = guestsData.data || guestsData;
            const totalGuests = document.getElementById('totalGuests');
            if (totalGuests) totalGuests.textContent = occupancy.booked_guest_count || 0;
            
            const revResponse = await apiRequest('/reports/revenue');
            const revData = await revResponse.json();
            const revenue = revData.data || revData;
            const totalRevenue = document.getElementById('totalRevenue');
            if (totalRevenue) totalRevenue.textContent = formatPeso(revenue.total_revenue);
        }
        
    } catch (error) {
        showMessage(`Error loading dashboard: ${error.message}`, 'error');
    }
}

// ============================================
// LOAD ROOMS WITH IMAGES - DEBUG VERSION
// ============================================
async function loadRooms() {
    console.log('✅ loadRooms called');
    try {
        const response = await apiRequest('/rooms');
        const data = await response.json();
        
        console.log('📦 Raw data type:', typeof data);
        console.log('📦 Raw data keys:', Object.keys(data));
        console.log('📦 Full data:', data);
        
        const grid = document.getElementById('roomGrid');
        if (!grid) {
            console.error('❌ roomGrid not found!');
            return;
        }
        
        // Try different ways to extract rooms
        let rooms = null;
        
        // Format 1: { data: { 1: {...}, 2: {...} } }
        if (data.data && typeof data.data === 'object') {
            rooms = data.data;
            console.log('✅ Format 1: data.data');
        }
        // Format 2: { 1: {...}, 2: {...} } (no wrapper)
        else if (typeof data === 'object' && !data.success && !data.message) {
            rooms = data;
            console.log('✅ Format 2: direct object');
        }
        // Format 3: { success: true, data: [array] }
        else if (data.success && Array.isArray(data.data)) {
            rooms = data.data;
            console.log('✅ Format 3: array in data');
        }
        // Format 4: { rooms: { 1: {...} } }
        else if (data.rooms) {
            rooms = data.rooms;
            console.log('✅ Format 4: rooms property');
        }
        // Fallback: use the whole response
        else {
            rooms = data;
            console.log('⚠️ Fallback: using entire response');
        }
        
        grid.innerHTML = '';
        
        // Check if rooms is empty or not an object
        if (!rooms || typeof rooms !== 'object' || Object.keys(rooms).length === 0) {
            console.log('❌ No rooms found in response');
            // Show raw data for debugging
            grid.innerHTML = `<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow: auto; font-size: 12px; max-height: 400px;">${JSON.stringify(data, null, 2)}</pre>`;
            return;
        }
        
        console.log(`✅ Found ${Object.keys(rooms).length} rooms`);
        
        const statusColors = {
            'AVAILABLE': '#2ecc71',
            'BOOKED': '#e74c3c',
            'MAINTENANCE': '#f39c12',
            'CLEANING': '#3498db'
        };
        
        for (const [id, room] of Object.entries(rooms)) {
            console.log(`🏠 Room ${room.room_number}: ${room.room_type}`);
            const color = statusColors[room.status] || '#95a5a6';
            const details = getRoomDetails(room);
            ROOM_AVAILABILITY[room.room_id || id] = room.availability || { booked_windows: [] };
            
            grid.innerHTML += `
                <div class="room-card">
                    <div class="room-image ${room.image_url ? '' : 'room-image-placeholder'}" aria-label="${escapeHtml(details.name)} image">
                        ${room.image_url
                            ? `<img src="${escapeHtml(room.image_url)}" alt="${escapeHtml(details.name)}" onerror="this.parentElement.classList.add('room-image-placeholder'); this.remove();">`
                            : `<span>${escapeHtml(details.name)} image placeholder</span>`}
                    </div>
                    <div class="room-info">
                        <p class="room-name">${escapeHtml(room.name || details.name)}</p>
                        <h3>Room ${room.room_number}</h3>
                        <p><strong>Room ID:</strong> ${room.room_id || id}</p>
                        <p class="room-description">${escapeHtml(room.details || `${details.type.toLowerCase()} room for up to ${details.capacity} guests.`)}</p>
                        <p><strong>Type:</strong> <span class="room-type-value">${escapeHtml(details.type)}</span></p>
                        <p><strong>Floor:</strong> ${room.floor}</p>
                        <p><strong>Capacity:</strong> ${details.capacity} guests</p>
                        <p><strong>Perks:</strong> ${escapeHtml(details.perks)}</p>
                        <p class="room-availability ${room.availability?.available_now ? 'is-available' : 'is-booked'}">
                            <strong>Availability:</strong> ${escapeHtml(room.availability?.label || (room.status === 'AVAILABLE' ? 'Available now' : room.status))}
                        </p>
                        ${room.availability?.available_now ? '' : `<p class="room-next-available"><strong>Next available:</strong> ${escapeHtml(room.availability.next_available)}</p>`}
                        <p class="room-price">From ${formatPeso(details.price)} / night</p>
                        <span class="status" style="background: ${color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; display: inline-block;">
                            <span class="room-status-value">${room.status}</span>
                        </span>
                        ${room.status !== 'MAINTENANCE' ? `
                            <button onclick="bookRoomById(${room.room_id})" class="book-btn" style="margin-top: 10px; width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                ${isAdmin && isAdmin() ? 'Book for Guest' : 'Book Now'}
                            </button>
                        ` : ''}
                        ${isAdmin && isAdmin() ? `
                            <button onclick="editRoom(${room.room_id})" class="room-edit-btn">
                                Edit Room
                            </button>
                            <button onclick="deleteRoom(${room.room_id})" class="room-delete-btn">
                                Delete Room
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        console.log(`✅ Displayed ${Object.keys(rooms).length} rooms`);
        
    } catch (error) {
        console.error('❌ Error loading rooms:', error);
        const grid = document.getElementById('roomGrid');
        if (grid) {
            grid.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
        showMessage(`Error loading rooms: ${error.message}`, 'error');
    }
}

function editRoom(roomId) {
    const room = document.querySelector(`[onclick="editRoom(${roomId})"]`)?.closest('.room-card');
    if (!room) return;

    document.getElementById('editRoomId').value = roomId;
    document.getElementById('editRoomName').value = room.querySelector('.room-name')?.textContent || '';
    document.getElementById('editRoomType').value = room.querySelector('.room-type-value')?.textContent || 'STANDARD';
    document.getElementById('editRoomStatus').value = room.querySelector('.room-status-value')?.textContent || 'AVAILABLE';
    document.getElementById('editRoomImage').value = '';
    document.getElementById('editRoomDetails').value = room.querySelector('.room-description')?.textContent || '';
    document.getElementById('editRoomForm').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function deleteRoom(roomId) {
    const roomCard = document.querySelector(`[onclick="deleteRoom(${roomId})"]`)?.closest('.room-card');
    const roomName = roomCard?.querySelector('.room-name')?.textContent || `Room ${roomId}`;
    if (!confirm(`Delete ${roomName}? Rooms with booking history cannot be deleted.`)) return;
    try {
        const response = await apiRequest(`/rooms/${roomId}`, { method: 'DELETE' });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Room deletion failed');
        showMessage('Room deleted successfully.', 'success');
        await loadRooms();
        await loadDashboard();
    } catch (error) {
        showMessage(`Error deleting room: ${error.message}`, 'error');
    }
}

async function submitRoomForm(event, mode) {
    event.preventDefault();
    const form = event.currentTarget;
    const isCreate = mode === 'create';
    const payload = isCreate
        ? {
            roomNumber: Number(document.getElementById('newRoomNumber').value),
            name: document.getElementById('newRoomName').value,
            roomType: document.getElementById('newRoomType').value,
            floor: Number(document.getElementById('newRoomFloor').value),
            imageUrl: document.getElementById('newRoomImage').value,
            details: document.getElementById('newRoomDetails').value
        }
        : {
            name: document.getElementById('editRoomName').value,
            roomType: document.getElementById('editRoomType').value,
            status: document.getElementById('editRoomStatus').value,
            imageUrl: document.getElementById('editRoomImage').value,
            details: document.getElementById('editRoomDetails').value
        };
    const endpoint = isCreate ? '/rooms' : `/rooms/${document.getElementById('editRoomId').value}`;
    try {
        const response = await apiRequest(endpoint, {
            method: isCreate ? 'POST' : 'PUT',
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Room update failed');
        form.reset();
        showMessage(isCreate ? 'Room added successfully.' : 'Room updated successfully.', 'success');
        await loadRooms();
    } catch (error) {
        showMessage(`Error saving room: ${error.message}`, 'error');
    }
}

// ============================================
// BOOK ROOM BY ID
// ============================================
async function bookRoomById(roomId) {
    const user = getUser();
    const adminUser = isAdmin && isAdmin();
    const room = document.querySelector(`[onclick="bookRoomById(${roomId})"]`)?.closest('.room-card');
    const roomName = room?.querySelector('.room-name')?.textContent || `Room ${roomId}`;
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
    const availability = ROOM_AVAILABILITY[roomId] || { booked_windows: [] };
    const lockedWindows = availability.booked_windows || [];
    const lockedText = `
        <div class="availability-calendar">
            <strong>Room availability</strong>
            ${lockedWindows.length
                ? lockedWindows.map(window => `
                    <div class="availability-row unavailable">
                        <span class="availability-dot"></span>
                        <span>${window.check_in} ${window.check_in_time} - ${window.check_out} ${window.check_out_time}</span>
                        <b>Booked</b>
                    </div>
                `).join('')
                : ''}
            <div class="availability-row available">
                <span class="availability-dot"></span>
                <span>Outside booked periods</span>
                <b>Available</b>
            </div>
        </div>
    `;
    let guestField = '';
    if (adminUser) {
        let guestOptions = '<option value="">Select a guest</option>';
        try {
            const guestsResponse = await apiRequest('/guests');
            const guestsData = await guestsResponse.json();
            const guests = guestsData.data || guestsData;
            guestOptions += Object.values(guests || {}).map(guest =>
                `<option value="${guest.guest_id}">${escapeHtml(`${guest.first_name} ${guest.last_name}`)} (ID: ${guest.guest_id})</option>`
            ).join('');
        } catch (error) {
            showMessage(`Could not load guests: ${error.message}`, 'error');
            return;
        }
        guestField = `
            <label for="bookingGuestId">Guest</label>
            <select id="bookingGuestId" name="guestId" required>${guestOptions}</select>
        `;
    }

    const modal = document.createElement('div');
    modal.className = 'booking-modal-backdrop';
    modal.innerHTML = `
        <form class="booking-modal" id="bookingForm">
            <button type="button" class="booking-modal-close" aria-label="Close">&times;</button>
            <h2>Book ${escapeHtml(roomName)}</h2>
            <p class="booking-modal-subtitle">Choose your stay details</p>
            ${lockedText}
            ${guestField}
            <label for="bookingCheckIn">Check-in date</label>
            <input id="bookingCheckIn" name="checkIn" type="date" min="${today}" value="${tomorrow}" required>
            <label for="bookingCheckOut">Check-out date</label>
            <input id="bookingCheckOut" name="checkOut" type="date" min="${tomorrow}" value="${new Date(Date.now() + 2 * 86400000).toISOString().split('T')[0]}" required>
            <label for="bookingCheckInTime">Check-in time</label>
            <input id="bookingCheckInTime" name="checkInTime" type="time" value="14:00" required>
            <label for="bookingCheckOutTime">Check-out time</label>
            <input id="bookingCheckOutTime" name="checkOutTime" type="time" value="12:00" required>
            <label for="bookingGuestCount">Number of guests</label>
            <input id="bookingGuestCount" name="guestCount" type="number" min="1" max="8" value="1" required>
            <label for="bookingRequests">Special requests <span>(optional)</span></label>
            <textarea id="bookingRequests" name="specialRequests" rows="3" maxlength="500" placeholder="Early check-in, extra pillows..."></textarea>
            <p class="booking-form-error" id="bookingFormError" role="alert"></p>
            <div class="booking-modal-actions">
                <button type="button" class="booking-secondary" id="bookingCancel">Cancel</button>
                <button type="submit" class="book-btn">Confirm booking</button>
            </div>
        </form>
    `;
    document.body.appendChild(modal);

    const closeModal = () => modal.remove();
    modal.querySelector('.booking-modal-close').addEventListener('click', closeModal);
    modal.querySelector('#bookingCancel').addEventListener('click', closeModal);
    modal.addEventListener('click', event => {
        if (event.target === modal) closeModal();
    });

    modal.querySelector('#bookingForm').addEventListener('submit', async event => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const checkIn = form.get('checkIn');
        const checkOut = form.get('checkOut');
        const checkInTime = form.get('checkInTime');
        const checkOutTime = form.get('checkOutTime');
        const error = modal.querySelector('#bookingFormError');
        if (checkOut < checkIn || (checkOut === checkIn && checkOutTime <= checkInTime)) {
            error.textContent = 'Check-out must be after check-in.';
            return;
        }

        const start = new Date(`${checkIn}T${checkInTime}`);
        const end = new Date(`${checkOut}T${checkOutTime}`);
        const overlapsLockedWindow = lockedWindows.some(window => {
            const lockedStart = new Date(`${window.check_in}T${window.check_in_time}`);
            const lockedEnd = new Date(`${window.check_out}T${window.check_out_time}`);
            return start < lockedEnd && end > lockedStart;
        });
        if (overlapsLockedWindow) {
            error.textContent = 'Those dates and times are locked because the room is already booked.';
            return;
        }

        const submitButton = modal.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Booking...';

        try {
            const response = await apiRequest('/bookings', {
                method: 'POST',
                body: JSON.stringify({
                    guestId: form.get('guestId') ? parseInt(form.get('guestId'), 10) : null,
                    roomId: roomId,
                    checkIn: checkIn,
                    checkOut: checkOut,
                    checkInTime: checkInTime,
                    checkOutTime: checkOutTime,
                    guestCount: parseInt(form.get('guestCount'), 10),
                    specialRequests: form.get('specialRequests') || ''
                })
            });
            const data = await response.json();
            if (!data.success) throw new Error(data.error || 'Booking failed');

            closeModal();
            showMessage(`Booking created successfully! ID: ${data.data.booking_id}`, 'success');
            loadRooms();
            loadDashboard();
        } catch (error) {
            modal.querySelector('#bookingFormError').textContent = error.message;
            submitButton.disabled = false;
            submitButton.textContent = 'Confirm booking';
        }
    });
}

// ============================================
// LOAD MY BOOKINGS
// ============================================
async function loadMyBookings() {
    try {
        const user = getUser();
        const endpoint = user && user.guest_id
            ? `/bookings/guest/${user.guest_id}`
            : '/bookings';
        const response = await apiRequest(endpoint);
        const data = await response.json();
        const bookingData = data.data || data;
        let bookings = Array.isArray(bookingData)
            ? bookingData
            : Object.values(bookingData || {});
        const guestLookup = {};
        if (isAdmin && isAdmin()) {
            const guestsResponse = await apiRequest('/guests');
            const guestsData = await guestsResponse.json();
            Object.values(guestsData.data || guestsData || {}).forEach(guest => {
                guestLookup[guest.guest_id] = `${guest.first_name} ${guest.last_name}`;
            });
        }
        const search = document.getElementById('bookingSearch')?.value.trim().toLowerCase() || '';
        const statusFilter = document.getElementById('bookingStatusFilter')?.value || '';
        const dateFilter = document.getElementById('bookingDateFilter')?.value || '';
        bookings = bookings.filter(booking => {
            const matchesSearch = !search || String(booking.booking_id).includes(search) || String(booking.room_number).includes(search);
            const matchesStatus = !statusFilter || booking.status === statusFilter;
            const matchesDate = !dateFilter || booking.check_in === dateFilter || booking.check_out === dateFilter;
            return matchesSearch && matchesStatus && matchesDate;
        });
        const tbody = document.getElementById('bookingTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!bookings || bookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="12" style="text-align: center;">No bookings found</td></tr>';
            renderBookingPagination(0);
            return;
        }
        const pageCount = Math.ceil(bookings.length / bookingPageSize);
        bookingPage = Math.min(bookingPage, pageCount);
        const visibleBookings = bookings.slice((bookingPage - 1) * bookingPageSize, bookingPage * bookingPageSize);

        for (const booking of visibleBookings) {
            const roomType = booking.room_type || booking.roomType || 'STANDARD';
            const roomDetails = ROOM_DETAILS[roomType] || ROOM_DETAILS.STANDARD;
            const canCancel = booking.status === 'CONFIRMED' && !booking.payment_id;
            const status = booking.status || 'UNKNOWN';
            const statusLabel = status.replaceAll('_', ' ');
            tbody.innerHTML += `
                <tr>
                    <td>${booking.booking_id || booking.bookingId || 'N/A'}</td>
                    <td>${escapeHtml(guestLookup[booking.guest_id] || (booking.guest_id ? `Guest ID ${booking.guest_id}` : 'N/A'))}</td>
                    <td>${booking.room_number || booking.roomNumber || 'N/A'}</td>
                    <td>${escapeHtml(roomType)}</td>
                    <td>${roomDetails.capacity} guests</td>
                    <td>${escapeHtml(roomDetails.perks)}</td>
                    <td>${booking.guest_count || booking.guestCount || 'N/A'}</td>
                    <td>${booking.check_in || booking.checkIn || 'N/A'}</td>
                    <td>${booking.check_out || booking.checkOut || 'N/A'}</td>
                    <td><span class="booking-status status-${status.toLowerCase()}">${escapeHtml(statusLabel)}</span></td>
                    <td>${formatPeso(booking.total_amount || booking.totalAmount)}</td>
                    <td>
                        ${canCancel ? `
                            <button onclick="cancelMyBooking(${booking.booking_id || booking.bookingId})" class="btn-cancel" style="padding: 5px 12px; background: #e74c3c; color: white; border: none; border-radius: 3px; cursor: pointer;">
                                Cancel
                            </button>
                        ` : '—'}
                    </td>
                </tr>
            `;
        }
        renderBookingPagination(pageCount);
    } catch (error) {
        showMessage(`Error loading bookings: ${error.message}`, 'error');
    }
}

function renderBookingPagination(pageCount) {
    const pagination = document.getElementById('bookingPagination');
    if (!pagination) return;
    pagination.innerHTML = pageCount > 1
        ? `<button type="button" ${bookingPage === 1 ? 'disabled' : ''} onclick="changeBookingPage(-1)">Previous</button><span>Page ${bookingPage} of ${pageCount}</span><button type="button" ${bookingPage === pageCount ? 'disabled' : ''} onclick="changeBookingPage(1)">Next</button>`
        : '';
}

function changeBookingPage(direction) {
    bookingPage += direction;
    loadMyBookings();
}

// ============================================
// CANCEL MY BOOKING
// ============================================
async function cancelMyBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    
    try {
        const response = await apiRequest('/bookings/cancel', {
            method: 'POST',
            body: JSON.stringify({ bookingId: bookingId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(`Booking ${bookingId} cancelled successfully!`, 'success');
            await loadMyBookings();
            await loadDashboard();
        } else {
            showMessage(`Error: ${data.error || 'Cancellation failed'}`, 'error');
        }
    } catch (error) {
        showMessage(`Error cancelling booking: ${error.message}`, 'error');
    }
}

// ============================================
// GUESTS (Admin)
// ============================================
async function loadGuests() {
    try {
        const response = await apiRequest('/guests');
        const data = await response.json();
        const guests = data.data || data;
        const tbody = document.getElementById('guestTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        const search = document.getElementById('guestSearch')?.value.trim().toLowerCase() || '';
        const guestRows = Object.values(guests || {}).filter(guest => {
            const text = `${guest.first_name} ${guest.last_name} ${guest.email} ${guest.phone}`.toLowerCase();
            return !search || text.includes(search);
        });

        if (guestRows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No guests found</td></tr>';
            return;
        }
        
        for (const guest of guestRows) {
            tbody.innerHTML += `
                <tr>
                    <td>${guest.guest_id || 'N/A'}</td>
                    <td>${guest.first_name || ''} ${guest.last_name || ''}</td>
                    <td>${guest.email || 'N/A'}</td>
                    <td>${guest.phone || 'N/A'}</td>
                    <td>${guest.bookings ? guest.bookings.length : 0}</td>
                    <td><button class="table-action-btn" onclick="editGuest(${guest.guest_id})">Edit</button><button class="table-action-btn danger" onclick="deleteGuest(${guest.guest_id})">Delete</button></td>
                </tr>
            `;
        }
    } catch (error) {
        showMessage(`Error loading guests: ${error.message}`, 'error');
    }
}

async function editGuest(guestId) {
    const firstName = prompt('First name:');
    if (firstName === null) return;
    const lastName = prompt('Last name:');
    if (lastName === null) return;
    const email = prompt('Email:');
    if (email === null) return;
    const phone = prompt('Phone:');
    if (phone === null) return;
    try {
        const response = await apiRequest(`/guests/${guestId}`, {
            method: 'PUT',
            body: JSON.stringify({ firstName, lastName, email, phone })
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Guest update failed');
        showMessage('Guest updated successfully.', 'success');
        await loadGuests();
    } catch (error) {
        showMessage(`Error updating guest: ${error.message}`, 'error');
    }
}

async function deleteGuest(guestId) {
    if (!confirm(`Delete guest ${guestId}? Guests with booking history cannot be deleted.`)) return;
    try {
        const response = await apiRequest(`/guests/${guestId}`, { method: 'DELETE' });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Guest deletion failed');
        showMessage('Guest deleted successfully.', 'success');
        await loadGuests();
    } catch (error) {
        showMessage(`Error deleting guest: ${error.message}`, 'error');
    }
}

async function submitGuestForm(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
        firstName: document.getElementById('newGuestFirstName').value,
        lastName: document.getElementById('newGuestLastName').value,
        email: document.getElementById('newGuestEmail').value,
        phone: document.getElementById('newGuestPhone').value,
        address: document.getElementById('newGuestAddress').value
    };
    try {
        const response = await apiRequest('/guests', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Guest creation failed');
        form.reset();
        showMessage('Guest added successfully.', 'success');
        await loadGuests();
    } catch (error) {
        showMessage(`Error adding guest: ${error.message}`, 'error');
    }
}

// ============================================
// PAYMENTS (Admin)
// ============================================
async function loadPayments() {
    try {
        const [paymentsResponse, bookingsResponse] = await Promise.all([
            apiRequest('/payments'),
            apiRequest('/bookings')
        ]);
        const paymentData = await paymentsResponse.json();
        const bookingData = await bookingsResponse.json();
        const payments = paymentData.data || paymentData;
        const bookings = bookingData.data || bookingData;
        const tbody = document.getElementById('paymentTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';

        const paymentRows = Object.values(payments || {});
        const recordedBookingIds = new Set(paymentRows.map(payment => String(payment.booking_id)));
        const unpaidRows = Object.values(bookings || {})
            .filter(booking => booking.status !== 'CANCELLED' && !recordedBookingIds.has(String(booking.booking_id)))
            .map(booking => ({
                payment_id: 'Pending',
                booking_id: booking.booking_id,
                amount: booking.total_amount,
                payment_method: 'Not recorded',
                status: 'UNPAID',
                transaction_date: 'Awaiting payment',
                unpaid: true
            }));
        const rows = [...paymentRows, ...unpaidRows];

        if (rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No payments found</td></tr>';
            return;
        }
        
        for (const payment of rows) {
            tbody.innerHTML += `
                <tr>
                    <td>${payment.payment_id || 'N/A'}</td>
                    <td>${payment.booking_id || 'N/A'}</td>
                    <td>${formatPeso(payment.amount)}</td>
                    <td>${payment.payment_method || 'N/A'}</td>
                    <td>${payment.status || 'N/A'}</td>
                    <td>${payment.unpaid
                        ? `<button class="payment-action-btn" onclick="fillPaymentForm(${payment.booking_id}, ${payment.amount})">Record payment</button>`
                        : payment.transaction_date || 'N/A'}</td>
                    <td>${payment.status === 'PAID' ? `<button class="table-action-btn danger" onclick="refundPayment(${payment.payment_id})">Refund</button>` : '—'}</td>
                </tr>
            `;
        }
    } catch (error) {
        showMessage(`Error loading payments: ${error.message}`, 'error');
    }
}

async function refundPayment(paymentId) {
    if (!confirm(`Refund payment ${paymentId}?`)) return;
    try {
        const response = await apiRequest('/payments/refund', {
            method: 'POST',
            body: JSON.stringify({ paymentId })
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Refund failed');
        showMessage('Payment refunded successfully.', 'success');
        await loadPayments();
        await loadDashboard();
        await loadRooms();
    } catch (error) {
        showMessage(`Error refunding payment: ${error.message}`, 'error');
    }
}

function fillPaymentForm(bookingId, amount) {
    document.getElementById('paymentBookingId').value = bookingId;
    document.getElementById('paymentAmount').value = amount;
    document.getElementById('paymentForm').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function submitPayment(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const bookingId = Number(document.getElementById('paymentBookingId').value);
    const amount = Number(document.getElementById('paymentAmount').value);
    const paymentMethod = document.getElementById('paymentMethod').value;

    try {
        const response = await apiRequest('/payments', {
            method: 'POST',
            body: JSON.stringify({ bookingId, amount, paymentMethod })
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.error || 'Payment failed');
        form.reset();
        showMessage('Payment recorded successfully.', 'success');
        await loadPayments();
        await loadDashboard();
    } catch (error) {
        showMessage(`Error recording payment: ${error.message}`, 'error');
    }
}

// ============================================
// REPORTS (Admin)
// ============================================
async function loadReports() {
    try {
        const reportDiv = document.getElementById('reportContent');
        if (!reportDiv) return;
        
        reportDiv.innerHTML = 'Loading report...';
        
        const response = await apiRequest('/reports/full');
        const data = await response.json();
        const report = data.data || data;
        
        const occupancy = report.occupancy || {};
        const revenue = report.revenue || {};
        const guests = report.guests || {};
        const bookings = report.bookings || {};
        reportDiv.innerHTML = `
            <div class="report-card"><h3>Occupancy</h3><p><strong>${occupancy.booked_rooms || 0}</strong> of ${occupancy.total_rooms || 0} rooms booked</p><p>${occupancy.booked_guest_count || 0} guests, ${occupancy.occupancy_rate || 0}% room occupancy</p></div>
            <div class="report-card"><h3>Revenue</h3><p class="report-value">${formatPeso(revenue.total_revenue)}</p><p>${revenue.bookings_count || 0} active bookings</p><p>Average: ${formatPeso(revenue.average_booking_value)}</p></div>
            <div class="report-card"><h3>Guests</h3><p><strong>${guests.total_guests || 0}</strong> registered guests</p><p>${guests.guests_with_bookings || 0} with bookings</p></div>
            <div class="report-card"><h3>Bookings</h3><p><strong>${bookings.total_bookings || 0}</strong> total bookings</p><p>Confirmed: ${bookings.status_counts?.CONFIRMED || 0}</p><p>Cancelled: ${bookings.status_counts?.CANCELLED || 0}</p></div>
        `;
    } catch (error) {
        showMessage(`Error loading reports: ${error.message}`, 'error');
    }
}

// ============================================
// TAB SWITCHING
// ============================================
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const tab = this.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        const target = document.getElementById(`tab-${tab}`);
        if (target) target.classList.add('active');
        
        // Load content based on tab
        if (tab === 'dashboard') loadDashboard();
        if (tab === 'rooms') loadRooms();
        if (tab === 'bookings') loadMyBookings();
        if (tab === 'guests') loadGuests();
        if (tab === 'payments') loadPayments();
        if (tab === 'reports') loadReports();
    });
});

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    setupRoleBasedUI();
    loadDashboard();

    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) paymentForm.addEventListener('submit', submitPayment);
    const createGuestForm = document.getElementById('createGuestForm');
    if (createGuestForm) createGuestForm.addEventListener('submit', submitGuestForm);
    const createRoomForm = document.getElementById('createRoomForm');
    if (createRoomForm) createRoomForm.addEventListener('submit', event => submitRoomForm(event, 'create'));
    const editRoomForm = document.getElementById('editRoomForm');
    if (editRoomForm) editRoomForm.addEventListener('submit', event => submitRoomForm(event, 'edit'));
    ['bookingSearch', 'bookingStatusFilter', 'bookingDateFilter'].forEach(id => {
        const control = document.getElementById(id);
        if (control) control.addEventListener('input', () => {
            bookingPage = 1;
            loadMyBookings();
        });
    });
    const clearBookingFilters = document.getElementById('clearBookingFilters');
    if (clearBookingFilters) clearBookingFilters.addEventListener('click', () => {
        document.getElementById('bookingSearch').value = '';
        document.getElementById('bookingStatusFilter').value = '';
        document.getElementById('bookingDateFilter').value = '';
        bookingPage = 1;
        loadMyBookings();
    });
    const guestSearch = document.getElementById('guestSearch');
    if (guestSearch) guestSearch.addEventListener('input', loadGuests);
    
    // Check if we're on dashboard page
    if (document.querySelector('.container')) {
        // Only set dates if elements exist
        const checkIn = document.getElementById('checkIn');
        const checkOut = document.getElementById('checkOut');
        
        if (checkIn && checkOut) {
            const today = new Date().toISOString().split('T')[0];
            const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
            checkIn.value = today;
            checkOut.value = tomorrow;
        }
    }
});

console.log('✅ App.js loaded successfully!');