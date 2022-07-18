
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //receive details from server
    socket.on('newnumber', function(msg) {
        // console.log("Received number" + msg.number);
        // //maintain a list of ten numbers
        // if (numbers_received.length >= 10){
        //     numbers_received.shift()
        // }            
        // numbers_received.push(msg.number);
        // numbers_string = '';
        // for (var i = 0; i < numbers_received.length; i++){
        //     numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        // }

        if(msg.items.length != 0){
            table = '<table id="editable" class="pure-table pure-table-bordered" style="width:100%">'

            // table += '<thead><tr><th>Products</th><th>Amounts</th><th>Price</th></tr></thead>'
            if(msg.items[0][0][2]=='/'){
                table+= '<thead><tr><th>Date</th><th>Money</th><th>Balance</th></tr></thead>'
            }
            else{
                table += '<thead><tr><th>Products</th><th>Amounts</th><th>Price</th></tr></thead>'
            }

            table += '<tbody>'
            for (var i = 0; i < msg.items.length; i++){
                table += '<tr><td>'+msg.items[i][0]+'</td><td>'+msg.items[i][1]+'</td><td>'+msg.items[i][2]+'</td></tr>'
            }
            table += '</tbody>'
            table += '</table>'
            
        }
        else{
            table = '<table></table>'

        }

        

        // img64 = 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
        img64 = msg.qr

        // $('#log').html(msg.number.toString());
        
        $('#log').html(table);
        $('#log3').html(msg.total.toString());  // total
        $('#log2').html(msg.customer);  //customer  // $('#log2').html(msg.total.toString());
        $('#log4').html(msg.status);  //status 
        
        document.getElementById("img").src = "data:image/png;base64,"+img64
    });

});