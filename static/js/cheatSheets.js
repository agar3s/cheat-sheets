var index = 0;
var removeVariable = function(indexSelected){
    $("#group"+indexSelected).remove();
};

var addVariable = function(){
    index++;
    $("#variables").append('<div id="groupfield'+index+'" class="control-group">'+
            '<input id="key'+index+'" name="key'+index+'" class="input-large key" type="text" placeholder="key">'+
            '<input id="value'+index+'" name="value'+index+'" class="input-xxlarge value" type="text" placeholder="value">'+
            '<button id="field'+index+'" class="btn btn-danger btn-small" type="submit"><i class="icon-remove icon-white"></i></button>'+
        '</div>');

    $("#field"+index).on("click",function(){
        removeVariable(this.id);
        return false;
    });

    $("#key"+index).on("keypress", function(e){
        if(e.which == 13) {
            $(this).next(".value").focus();
            return false;
        }
    });

    $("#value"+index).on("keypress", function(e) {
        var keyCode = e.keyCode || e.which;
        if(keyCode == 13 || keyCode == 9) {
            e.preventDefault();
            addVariable();
            $("#key"+index).focus();
            return false;
        }
    });
};

(function(){

    index = $(".key").length;

    $(".remove").on("click",function(){
        removeVariable(this.id);
        return false;
    });

    $(".key").on("keypress", function(e){
        if(e.which == 13) {
            $(this).next(".value").focus();
            return false;
        }
    });

    $(".value").on("keypress", function(e) {
        var keyCode = e.keyCode || e.which;
        if(keyCode == 13 || keyCode == 9) {
            e.preventDefault();
            addVariable();
            return false;
        }
    });

    $("#add").on("click",function(){
        addVariable();
        return false;
    });

    $("#name").on("keypress", function(e){
            if(e.which == 13) {
                $("#key1").focus();
                return false;
            }
        });

    $(document).bind('keyup keydown', function(e){
        if(e.shiftKey){
            if((e.keyCode || e.which) == 13){
                $("#cheat-sheet").submit();
            }
        }

    });

})();