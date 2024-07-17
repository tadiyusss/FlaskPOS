var cart = {};
let notificationCount = 0;

function get_total(){
    var total = 0;
    for(var i = 0; i < Object.keys(cart).length; i++){
        total += cart[Object.keys(cart)[i]]['price'] * cart[Object.keys(cart)[i]]['quantity']
    }
    return total.toFixed(2)
}

function get_change(){
    var tendered = $('#tendered').val();
    var total = get_total();
    var change = tendered - total;
    return change.toFixed(2)
}

function update_change(){
    var tendered = $('#tendered').val();
    var total = get_total();
    var change = tendered - total;
    $('#change').text(change.toFixed(2))
}

function update_checkout_btn(){
    if (Object.keys(cart).length > 0 && get_change() >= 0 ){
        $("#checkout_btn").prop('disabled', false)
    } else {
        $("#checkout_btn").prop('disabled', true)
    }
}


function update_cart(){
    var cart_container = $('#cart_container');
    cart_container.empty();
    if (Object.keys(cart).length > 0){
        update_checkout_btn()
        for(var i = 0; i < Object.keys(cart).length; i++){
            cart_container.append(`
                <div class="w-full p-3 flex items-center justify-between rounded dark:border-0 bg-gray-100 dark:bg-slate-700 mb-2">
                    <svg data-product-id="${Object.keys(cart)[i]}" id="decrease_quantity" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="cursor-pointer text-gray-500 size-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                    </svg>
                    <h5 class="max-w-40 truncate">${cart[Object.keys(cart)[i]]['name']}</h5>
                    <h5>${cart[Object.keys(cart)[i]]['quantity']}</h5>
                    <h5>${(cart[Object.keys(cart)[i]]['quantity'] * cart[Object.keys(cart)[i]]['price']).toFixed(2)}</h5>
                </div>
            `)
        }
    } else {
        update_checkout_btn()
        cart_container.append('<p class="text-center my-2 text-gray-500">Your cart is empty</p>')
    }

    $('#cart_total').text(get_total())
    $('#change').text(get_change())
}

$('#tendered').on('input', function() {
    update_checkout_btn()
    $('#change').text(get_change())
});

$('#cart_container').on('click', '#decrease_quantity', function() {
    var product_id = $(this).attr('data-product-id');
    if (cart[product_id]['quantity'] > 1){
        cart[product_id]['quantity'] -= 1;
    } else {
        delete cart[product_id]
    }
    update_cart()
});

$('#category_list').on('change', function(){
    var category_id = $(this).val();
    $.ajax({
        type: 'GET',
        url: '/api/pos/get_product/category_id/' + category_id,
        success: function(response){
            if (response['status'] == 'success'){
                if (response['data'].length > 0) {
                    $("#products_card_container").empty();
                    rows = response['data']
                    rows.forEach(row => {
                        $("#products_card_container").append(`
                            <div class="col-span-1 p-1 dark:text-slate-100 bg-gray-50 dark:bg-slate-700 dark:hover:bg-slate-600 dark:border-slate-500 dark:border-0 border rounded cursor-pointer hover:bg-gray-100 ease duration-200" id="product_card" data-product-id="${row['id']}">
                                <img class="w-20 h-20 mx-auto object-cover" src="/static/pos/products/${row['filename']}" alt="">
                                <div class="text-center mt-2">
                                    <h5 class="text-sm leading-3" id="product_name">${row['product_name']}</h5>
                                    <p class="text-xs text-slate-500" id="product_price">₱${row['price']}</p>
                                </div>
                            </div>    
                        `)
                    });
                } else {
                    $("#products_card_container").html('<p class="text-center my-10 text-gray-500 col-span-6">No products available</p>')
                }
            }
        }
    })
})

$('#products_card_container').on('click', '#product_card', function() {
    var product_id = $(this).attr('data-product-id');
    $.ajax({
        type: 'GET',
        url: '/api/pos/get_product/product_id/' + product_id,
        success: function(response){
            if (response['status'] == 'success'){
                var product_data = response['data'];
                if (cart[product_data['id']]){
                    cart[product_data['id']]['quantity'] += 1;
                } else {
                    cart[product_data['id']] = {
                        'quantity': 1,
                        'price': product_data['price'],
                        'name': product_data['product_name']
                    }
                }
                update_cart()
                $('#cart_total').text(get_total())
            }
        }
    })

});

$("#checkout_btn").on('click', function(){
    console.log(cart)
    $.ajax({
        url: '/api/pos/checkout',
        type: 'POST',
        data: {
            'cart': JSON.stringify(cart),
            'tendered': $('#tendered').val()
        },
        success: function(response){
            if (response['status'] == 'success'){
                window.location.href = '/dashboard/pos/sales/view/' + response['sale_id']
            } else {
                showNotification(response['message'], 'bg-red-500', 'text-white')
            }
        }
    })
})


function showNotification(message, bgColor = 'bg-blue-500', textColor = 'text-white') {
    notificationCount++;
    const notificationId = 'notification-' + notificationCount;
    
    const notificationHtml = `
        <div id="${notificationId}" class="notification ${bgColor} ${textColor} px-4 py-2 rounded-lg shadow-lg">
            ${message}
        </div>
    `;
    
    $('#notifications-container').append(notificationHtml);
    
    $('#' + notificationId).fadeIn('slow').delay(3000).fadeOut('slow', function() {
        $(this).remove();
    });
}
$('#showNotification').click(function() {
    showNotification('This is a notification!', 'bg-yellow-200', 'text-dark');
});