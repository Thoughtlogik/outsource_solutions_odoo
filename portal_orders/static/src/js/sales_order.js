odoo.define('portal_orders.sales_order', function(require) {
	"use strict";
	var Animation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');



	var rpc = require('web.rpc');

	$(document).ready(function() {

		 
    
		$(".tag_ids").chosen({
				enable_search_threshold: 10
				
			});
			


$('#tag_ids').change (function () {
		var UserIds = $('#tag_ids').val();
		/*var ser_var=document.getElementById('tax_empty').value;
		ser_var = UserIds */
		 document.getElementById('tax_empty').value = UserIds
		console.log("assign",document.getElementById('tax_empty').value)
    });
		$('#add-line-btn').click(function() {

			$(".children_tax_ids").chosen({
				enable_search_threshold: 10
			});

		});


        $('#export').click(function () {
    console.log("cc");
    var checkedCheckboxes = document.querySelectorAll('.check:checked');
    console.log("Checked checkboxes:");
    var checkboxesChecked = [];
    checkedCheckboxes.forEach(function(checkbox) {
        var orderId = checkbox.getAttribute('data-id');
        console.log("Order ID:", orderId);
        checkboxesChecked.push(orderId);
    });
    console.log("checkboxesChecked:", checkboxesChecked);

    ajax.post("/export/timesheets/records", {'checked': checkboxesChecked}).then(function(result) {
        // Handle response here
    });
});

  //alert(result['result'])
// (C1) DUMMY DATA


//	var data = [["Date", "Employee", "Project", "Task", "Description", "Hours", "Project Type", "Activity Type", "Platform", "status"] ];
//
//	 var s = result; //" [{'id':1,'name':'Test1'},{'id':2,'name':'Test2'},{'id':3,'name':'Test3'},{'id':4,'name':'Test4'}]";
//	 var myObject = eval('(' + s + ')');
//		for (i in myObject)
//		{
//			var vals = []
//		    vals.push(myObject[i]["date"],myObject[i]["employee"],myObject[i]["project"],myObject[i]["task"],myObject[i]["description"],myObject[i]["hours"],myObject[i]["project_type"],myObject[i]["activity_type"],myObject[i]["platform"],myObject[i]["status"]);
//			data.push(vals)
//		}
//	// (C2) CREATE NEW EXCEL "FILE"
//	var workbook = XLSX.utils.book_new(),
//	    worksheet = XLSX.utils.aoa_to_sheet(data);
//	workbook.SheetNames.push("First");
//	workbook.Sheets["First"] = worksheet;
//
//	// (C3) "FORCE DOWNLOAD" XLSX FILE
//	XLSX.writeFile(workbook, "Timesheets.xlsx");
  //});

    /* ajax.post('/shop/cart/update_option', {})
                    .then(function (quantity) {
                        if (goToShop) {
                            window.location.pathname = "/shop/cart";
                        }
                        const $quantity = $(".my_cart_quantity");
                        $quantity.parent().parent().removeClass('d-none');
                        $quantity.text(quantity).hide().fadeIn(600);
                    });*/



//});
		

		/*$('#export').click(function () {
		console.log("dddd")
		 var partner = document.getElementById("cust").value;
		 var crmId = ''
         if (partner != ' ')
        	 return rpc.query({
		            model: "sale.order",
		            method: 'get_the_price_list',
		            args: [crmId,partner],
		            context: {},
		        }).then(function (data) {

					const price = document.getElementById("price")
					price.value = data
            });
			});*/
	});
});