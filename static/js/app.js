const state = {
    items: [],
    category: 'All',
    cart: JSON.parse(localStorage.getItem('streetbaik_cart') || '{}')
};

const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const money = (n) => '₹' + Number(n).toFixed(0);


// ================= LOAD MENU =================

async function load() {
    try {
        const r = await fetch('/api/menu/');
        const d = await r.json();

        state.items = d.items || [];

        renderChips(d.categories || []);
        renderMenu();
        renderCart();

    } catch (error) {
        console.error('Menu loading error:', error);

        if ($('#menuGrid')) {
            $('#menuGrid').innerHTML =
                '<p class="empty">Unable to load menu.</p>';
        }
    }
}


// ================= CATEGORY CHIPS =================

function renderChips(cats) {

    // Keep ALL category at the LAST position
    cats = [
        ...cats.filter(c => c.name !== 'All'),
        ...cats.filter(c => c.name === 'All')
    ];

    $('#chips').innerHTML = cats.map(c => `
        <button
            class="chip ${state.category === c.name ? 'active' : ''}"
            data-cat="${c.name}">
            ${c.icon || ''} ${c.name}
        </button>
    `).join('');

    $$('#chips .chip').forEach(button => {

        button.onclick = () => {

            state.category = button.dataset.cat;

            renderChips(cats);
            renderMenu();
        };

    });
}


// ================= MENU =================

function renderMenu() {

    const searchInput = $('#search');

    const q = searchInput
        ? searchInput.value.toLowerCase().trim()
        : '';

    let items = state.items.filter(item => {

        const categoryMatch =
            state.category === 'All' ||
            item.category === state.category;

        const searchMatch =
            item.name.toLowerCase().includes(q);

        return categoryMatch && searchMatch;
    });


    // Sorting
    const sort = $('#sort') ? $('#sort').value : '';

    if (sort === 'low') {
        items.sort((a, b) =>
            Number(a.price) - Number(b.price)
        );
    }

    if (sort === 'high') {
        items.sort((a, b) =>
            Number(b.price) - Number(a.price)
        );
    }


    if (!$('#menuGrid')) return;


    $('#menuGrid').innerHTML = items.map(item => `

        <article class="food-card">

            <div class="food-img">

                <img
                    src="/static/images/${item.image}"
                    alt="${item.name}"
                    loading="lazy">

                ${
                    item.bestseller
                        ? '<span class="badge">BESTSELLER</span>'
                        : ''
                }

            </div>


            <div class="food-body">

                <div class="tags">

                    <span>
                        ${
                            item.diet === 'veg'
                                ? 'VEG'
                                : 'NON-VEG'
                        }
                    </span>

                    <span>${item.category}</span>

                </div>


                <h3>${item.name}</h3>

                <p>${item.description || ''}</p>


                <div class="food-bottom">

                    <strong>
                        ${money(item.price)}
                    </strong>

                    <button
                        class="add"
                        data-id="${item.id}">
                        + Add to Cart
                    </button>

                </div>

            </div>

        </article>

    `).join('');


    if (!items.length) {
        $('#menuGrid').innerHTML =
            '<p class="empty">No dishes found.</p>';
    }


    $$('.add').forEach(button => {

        button.onclick = () => {

            add(button.dataset.id);

        };

    });
}


// ================= ADD TO CART =================

function add(id) {

    state.cart[id] =
        (state.cart[id] || 0) + 1;

    save();
    renderCart();
    openCart();
}


// ================= SAVE CART =================

function save() {

    localStorage.setItem(
        'streetbaik_cart',
        JSON.stringify(state.cart)
    );

    const count = Object.values(state.cart)
        .reduce((a, b) => a + b, 0);

    if ($('#cartCount')) {
        $('#cartCount').textContent = count;
    }
}


// ================= CART ROWS =================

function cartRows() {

    return Object.entries(state.cart)
        .map(([id, quantity]) => ({

            item: state.items.find(
                item => String(item.id) === String(id)
            ),

            q: quantity

        }))
        .filter(x => x.item);
}


// ================= CART TOTAL =================

function total() {

    return cartRows().reduce(
        (sum, x) =>
            sum + Number(x.item.price) * x.q,
        0
    );
}


// ================= RENDER CART =================

function renderCart() {

    save();

    if (!$('#cartItems')) return;

    const rows = cartRows();


    $('#cartItems').innerHTML = rows.map(x => `

        <div class="cart-row">

            <img
                src="/static/images/${x.item.image}"
                alt="${x.item.name}">

            <div>

                <b>${x.item.name}</b>

                <small>
                    ${money(x.item.price)} × ${x.q}
                </small>


                <div class="qty">

                    <button
                        data-dec="${x.item.id}">
                        −
                    </button>

                    <span>${x.q}</span>

                    <button
                        data-inc="${x.item.id}">
                        +
                    </button>

                    <button
                        class="remove"
                        data-rem="${x.item.id}">
                        Remove
                    </button>

                </div>

            </div>


            <strong>
                ${money(x.item.price * x.q)}
            </strong>

        </div>

    `).join('');


    if (!rows.length) {

        $('#cartItems').innerHTML = `
            <div class="empty">
                Your cart is empty.
            </div>
        `;

    }


    if ($('#cartTotal')) {
        $('#cartTotal').textContent = money(total());
    }


    // Increase

    $$('[data-inc]').forEach(button => {

        button.onclick = () => {

            const id = button.dataset.inc;

            state.cart[id]++;

            renderCart();
        };

    });


    // Decrease

    $$('[data-dec]').forEach(button => {

        button.onclick = () => {

            const id = button.dataset.dec;

            state.cart[id]--;

            if (state.cart[id] <= 0) {
                delete state.cart[id];
            }

            renderCart();
        };

    });


    // Remove

    $$('[data-rem]').forEach(button => {

        button.onclick = () => {

            const id = button.dataset.rem;

            delete state.cart[id];

            renderCart();
        };

    });
}


// ================= CART DRAWER =================

function openCart() {

    if ($('#drawer')) {
        $('#drawer').classList.add('open');
    }

    if ($('#drawerBg')) {
        $('#drawerBg').classList.add('show');
    }
}


function closeCart() {

    if ($('#drawer')) {
        $('#drawer').classList.remove('open');
    }

    if ($('#drawerBg')) {
        $('#drawerBg').classList.remove('show');
    }
}


// ================= SEARCH / SORT =================

if ($('#search')) {
    $('#search').oninput = renderMenu;
}

if ($('#sort')) {
    $('#sort').onchange = renderMenu;
}


// ================= CART BUTTONS =================

if ($('#cartOpen')) {
    $('#cartOpen').onclick = openCart;
}

if ($('#cartClose')) {
    $('#cartClose').onclick = closeCart;
}

if ($('#drawerBg')) {
    $('#drawerBg').onclick = closeCart;
}


// ================= CHECKOUT =================

if ($('#checkoutOpen')) {

    $('#checkoutOpen').onclick = () => {

        if (!cartRows().length) {

            alert('Your cart is empty.');

            return;
        }


        if ($('#checkoutSummary')) {

            $('#checkoutSummary').innerHTML =

                cartRows().map(x => `

                    <div class="summary-line">

                        <span>
                            ${x.item.name} × ${x.q}
                        </span>

                        <b>
                            ${money(x.item.price * x.q)}
                        </b>

                    </div>

                `).join('')

                +

                `

                <div class="summary-total">

                    <span>Total</span>

                    <b>${money(total())}</b>

                </div>

                `;
        }


        if ($('#checkoutModal')) {
            $('#checkoutModal').classList.add('show');
        }

        closeCart();
    };
}


// ================= CLOSE CHECKOUT =================

if ($('#checkoutClose')) {

    $('#checkoutClose').onclick = () => {

        $('#checkoutModal').classList.remove('show');

    };
}


// ================= ORDER TYPE =================

if ($('#orderType')) {

    $('#orderType').onchange = (e) => {

        if ($('#tableNo')) {

            $('#tableNo').placeholder =
                e.target.value === 'Dine-in'
                    ? 'Table number (if already seated)'
                    : 'Table number (optional)';

        }

    };
}


// ================= PLACE ORDER =================

if ($('#checkoutForm')) {

    $('#checkoutForm').onsubmit = async (e) => {

        e.preventDefault();


        const rows = cartRows();


        if (!rows.length) {

            $('#checkoutMsg').textContent =
                'Your cart is empty.';

            return;
        }


        const form = new FormData(e.target);

        const data =
            Object.fromEntries(form.entries());


        data.items = rows.map(x => ({

            id: x.item.id,
            quantity: x.q

        }));


        try {

            $('#checkoutMsg').textContent =
                'Placing your order...';


            // IMPORTANT:
            // Django URL has trailing slash

            const r = await fetch('/api/orders/', {

                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify(data)

            });


            const d = await r.json();


            console.log('Order response:', d);


            if (!r.ok || !d.ok) {

                $('#checkoutMsg').textContent =
                    d.error ||
                    'Unable to place order. Please try again.';

                return;
            }


            // Successful order

            state.cart = {};

            save();
            renderCart();


            $('#checkoutModal').classList.remove('show');


            $('#successText').textContent =
                `Order ${d.public_id} has been placed successfully. Total ${money(d.total)}.`;


            $('#trackLink').href =
                `/track?order=${d.public_id}`;


            $('#successModal').classList.add('show');


        } catch (error) {

            console.error(
                'Place order error:',
                error
            );

            $('#checkoutMsg').textContent =
                'Unable to connect to the server. Please try again.';

        }

    };
}


// ================= SUCCESS MODAL =================

if ($('#successClose')) {

    $('#successClose').onclick = () => {

        $('#successModal').classList.remove('show');

    };

}


// ================= GENERIC POST =================

async function postForm(form, url, msgEl) {

    try {

        const fd = new FormData(form);

        const data =
            Object.fromEntries(fd.entries());


        const r = await fetch(url, {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(data)

        });


        const d = await r.json();


        msgEl.textContent =
            d.ok
                ? 'Done ✓'
                : d.error || 'Something went wrong.';


        return d;


    } catch (error) {

        console.error(error);

        msgEl.textContent =
            'Something went wrong. Please try again.';


        return {
            ok: false,
            error: error.message
        };

    }
}


// ================= BOOKING =================

if ($('#bookingForm')) {

    $('#bookingForm').onsubmit = async (e) => {

        e.preventDefault();


        const d = await postForm(
            e.target,
            '/api/reservations/',
            $('#bookingMsg')
        );


        if (d.ok) {
            e.target.reset();
        }

    };

}


// ================= REVIEWS =================

if ($('#reviewForm')) {

    $('#reviewForm').onsubmit = async (e) => {

        e.preventDefault();


        const d = await postForm(
            e.target,
            '/api/reviews/',
            $('#reviewMsg')
        );


        if (d.ok) {
            e.target.reset();
        }

    };

}


// ================= CONTACT =================

if ($('#contactForm')) {

    $('#contactForm').onsubmit = async (e) => {

        e.preventDefault();


        const d = await postForm(
            e.target,
            '/api/messages/',
            $('#contactMsg')
        );


        if (d.ok) {
            e.target.reset();
        }

    };

}


// ================= START APP =================

load();