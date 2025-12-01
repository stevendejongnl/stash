async function fetchProducts() {
  const res = await fetch('/api/products');
  return res.json();
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/[&<>"']/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]);
}

function render(products) {
  const container = document.getElementById('products');
  if (!products.length) {
    container.innerHTML = '<p>No items yet — add something!</p>';
    return;
  }
  container.innerHTML = products.map(p => `
    <div class="product">
      <div class="left">
        ${p.image ? `<img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.title)}" />` : '<div class="no-img">No image</div>'}
      </div>
      <div class="right">
        <a class="title" href="${escapeHtml(p.url)}" target="_blank" rel="noopener">${escapeHtml(p.title)}</a>
        <div class="meta">
          <span class="price">${escapeHtml(p.price)}</span>
          <span class="date">${new Date(p.created_at).toLocaleString()}</span>
        </div>
        <p class="notes">${escapeHtml(p.notes)}</p>
        <button data-id="${p.id}" class="delete">Delete</button>
      </div>
    </div>
  `).join('');
}

async function loadAndRender() {
  const products = await fetchProducts();
  render(products);
}

document.getElementById('productForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = document.getElementById('title').value.trim();
  const url = document.getElementById('url').value.trim();
  const price = document.getElementById('price').value.trim();
  const image = document.getElementById('image').value.trim();
  const notes = document.getElementById('notes').value.trim();

  if (!title || !url) return alert('Title and URL are required.');

  const res = await fetch('/api/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, url, price, image, notes })
  });

  if (res.ok) {
    document.getElementById('productForm').reset();
    loadAndRender();
  } else {
    const err = await res.json();
    alert('Error: ' + (err.error || 'unknown'));
  }
});

document.getElementById('products').addEventListener('click', async (e) => {
  if (!e.target.classList.contains('delete')) return;
  const id = e.target.getAttribute('data-id');
  if (!confirm('Delete this item?')) return;
  const res = await fetch('/api/products/' + id, { method: 'DELETE' });
  if (res.ok) loadAndRender();
  else alert('Failed to delete');
});

// initial load
loadAndRender();