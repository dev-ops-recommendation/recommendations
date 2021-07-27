$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.product_id);
        $("#recommendation_product_id").val(res.recommendation_product_id);
        $("#relationship").val(res.relationship);
        $('#likescount').html(res.likes);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#recommendation_product_id").val("");
        $("#relationship").val("");
        $('#likescount').html("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        var product_id = $("#product_id").val();
        var recommendation_product_id = $("#recommendation_product_id").val();
        var relationship = $("#relationship").val();

        var data = {
            "product_id": product_id,
            "recommendation_product_id": recommendation_product_id,
            "relationship": relationship
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();
        
        var relationship = $("#relationship").val();
        var recommendation_product_id = $("#recommendation_product_id").val();

        var data = {
            "product_id": product_id,
            "recommendation_product_id": recommendation_product_id,
            "relationship": relationship
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/recommendations/" + product_id + "/recommended-products/" + recommendation_product_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recomendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();
        var recommendation_product_id = $("#recommendation_product_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations/" + product_id + "/recommended-products/" + recommendation_product_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();
        var recommendation_product_id = $("#recommendation_product_id").val();


        var ajax = $.ajax({
            type: "DELETE",
            url: "/recommendations/" + product_id + "/recommended-products/" + recommendation_product_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Like a Recommendation
    // ****************************************

    $("#like-btn").click(function () {

        var product_id = $("#product_id").val();
        var recommendation_product_id = $("#recommendation_product_id").val();


        var ajax = $.ajax({
            type: "PUT",
            url: "/recommendations/" + product_id + "/recommended-products/" + recommendation_product_id + "/like",
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Liked!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });


    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        var product_id = $("#product_id").val();
        var relationship = $("#relationship").val();
       
        var queryString = ""
        if (product_id) {
            queryString += "/" + product_id
        }
        if (relationship) {
            queryString += "?type=" + relationship
        }
    

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:50%">Recommendation Product ID</th>'
            header += '<th style="width:40%">Relationship</th>'
            header += '<th style="width:10%">Likes</th></tr>'
            $("#search_results").append(header);
            var firstRecommendation = "";
            for(var i = 0; i < res.length; i++) {
                var recommendation = res[i];
                var row = "<tr><td>"+recommendation.product_id+"</td><td>"+recommendation.recommendation_product_id+"</td><td>"+recommendation.relationship+"</td><td>"+recommendation.likes+"</td><td>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstRecommendation = recommendation;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstRecommendation != "") {
                update_form_data(firstRecommendation)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
