document.addEventListener('DOMContentLoaded', function () {
    const pollInterval = 15000; // 15 seconds

    async function fetchMovimientos(productoId) {
        let url = '/reportes/api/ultimos_movimientos/';
        if (productoId) url += '?producto=' + productoId;

        const resp = await fetch(url, { credentials: 'same-origin' });
        if (!resp.ok) return null;
        const json = await resp.json();
        return json.movimientos || [];
    }

    function renderDashboardTable(movimientos) {
        const tbody = document.querySelector('main .panel table.table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        movimientos.forEach(m => {
            const tr = document.createElement('tr');
            tr.dataset.href = m.detail_url || ('/reportes/kardex/?producto=' + m.producto_id);
            tr.innerHTML = `
                <td>${m.producto}</td>
                <td><span class="badge ${m.tipo === 'ENTRADA' ? 'bg-success' : 'bg-warning text-dark'}">${m.tipo}</span></td>
                <td>${m.cantidad}</td>
                <td>${m.fecha}</td>
            `;
            tbody.appendChild(tr);
        });
        attachRowHandlers();
    }

    function renderKardexTable(movimientos) {
        const tabla = document.getElementById('tablaKardex');
        if (!tabla) return;
        const tbody = tabla.querySelector('tbody');
        tbody.innerHTML = '';
        movimientos.forEach((m, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${idx+1}</td>
                <td>${m.fecha}</td>
                <td>${m.usuario || ''}</td>
                <td>${m.producto}</td>
                <td><span class="badge ${m.tipo === 'ENTRADA' ? 'bg-success' : 'bg-danger'}">${m.tipo}</span></td>
                <td>${m.cantidad}</td>
                <td>${m.stock_anterior || ''}</td>
                <td>${m.stock_nuevo || ''}</td>
            `;
            if (m.detail_url) tr.dataset.href = m.detail_url;
            tbody.appendChild(tr);
        });
        attachRowHandlers();
    }

    function attachRowHandlers() {
        const rows = document.querySelectorAll('table.table tbody tr[data-href]');
        rows.forEach(row => {
            row.style.cursor = 'pointer';
            row.onclick = () => { window.location.href = row.dataset.href; };
        });
    }

    async function pollAndUpdate() {
        const movimientos = await fetchMovimientos();
        if (movimientos) {
            renderDashboardTable(movimientos.slice(0,8));
        }

        // If on kardex page, also update its table
        const kardexTable = document.getElementById('tablaKardex');
        if (kardexTable) {
            const params = new URLSearchParams(window.location.search);
            const producto = params.get('producto');
            const movimientosK = await fetchMovimientos(producto);
            if (movimientosK) renderKardexTable(movimientosK);
        }
    }

    // initial
    pollAndUpdate();
    setInterval(pollAndUpdate, pollInterval);
});
