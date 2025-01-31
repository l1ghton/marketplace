// Обновление количества товара в корзине
document.querySelectorAll('.quantity').forEach(input => {
    input.addEventListener('change', (e) => {
        const productId = e.target.getAttribute('data-product-id');
        const quantity = e.target.value;
        fetch(`/update_cart/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity: quantity }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Обновляем страницу, чтобы отразить изменения
            } else {
                alert('Failed to update quantity.');
            }
        });
    });
});

// Удаление товара из корзины
document.querySelectorAll('.remove-from-cart').forEach(button => {
    button.addEventListener('click', () => {
        const productId = button.getAttribute('data-product-id');
        fetch(`/remove_from_cart/${productId}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Обновляем страницу, чтобы отразить изменения
            } else {
                alert('Failed to remove item from cart.');
            }
        });
    });
});