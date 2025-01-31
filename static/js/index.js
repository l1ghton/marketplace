// Добавление товара в корзину
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', () => {
        const productId = button.getAttribute('data-product-id');
        fetch(`/add_to_cart/${productId}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Product ${productId} added to cart!`);
                location.reload(); // Обновляем страницу, чтобы обновить количество товаров в корзине
            } else {
                alert('Failed to add product to cart.');
            }
        });
    });
});