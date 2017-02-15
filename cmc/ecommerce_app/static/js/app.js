/**
 * Created by Agustino on 12/05/16.
 */
$(function () {

    //AJAX config for using CSRF
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});

$('.subnav').on( 'affixed.bs.affix', function () {
    $('.affix-cart').show()
} );

$('.subnav').on( 'affixed-top.bs.affix', function () {
    $('.affix-cart').hide()
} );


// Subnavbar fixed top
$('.subnav').affix({
      offset: {
        top: $('#navtop').height()
      }
});



$('#contact_form').formValidation({
    framework: 'bootstrap',
    fields: {
        name: {
            validators: {
                notEmpty: {
                    message: 'El nombre es requerido'
                }
            }
        },
        last_name: {
            validators: {
                notEmpty: {
                    message: 'Apellido es requerido'
                }
            }
        },
        email: {
            validators: {
                notEmpty: {
                    message: 'El correo es requerido'
                },
                emailAddress: {
                        message: 'No es un formato de correo'
                }
            }
        },
        message: {
            validators: {
                notEmpty: {
                    message: 'El mensaje es requerido'
                },
            }
        }
    }
})

$('#edit_profile_form').formValidation({
       framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            email: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: 'Campo obligatorio.',
                    },
                    emailAddress: {
                        enabled: true
                    },
                    remote: {
                        type: "POST",
                        message: 'Este correo ya ha sido usado.',
                        url: '/user/check',
                        data: {
                            type: 'email',
                            csrfmiddlewaretoken:window.CSRF_TOKEN
                        }
                    }
                }
            },
            telephone: {
                validators: {
                    notEmpty: {
                        enabled: true
                    },
                    numeric: {
                        enabled: true,
                        message: "Introduce Solo números"
                    },
                }
            },
            first_name: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            last_name: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            second_last_name: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            nombre_empresa: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            direccion_calle: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            direccion_colonia: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            direccion_delegacion: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: "Campo reuqerido."
                    }
                }
            },
            direccion_cp: {
                validators: {
                    notEmpty: {
                        enabled: true
                    },
                    numeric: {
                        enabled: true,
                        message: "Introduce Solo números"
                    },
                    stringLength: {
                        max: 5,
                        min: 5,
                        message: 'El formato de cp es a 5 digitos.'
                    },
                    callback: {
                        message:'Codigo Postal Inv&aacute;lido',
                        callback: function(value, validator, $field){
                                var options = validator.getFieldElements('direccion_cp').val();
                                return(options[0] !== "0" || options[1] !== "0");
                        }
                    }
                }
            },
        }
    });





$(document).ready(function() {
  $("select").select2();
});

$('.upload').on('change', function(){
    var valor = this.value
    var id_image = ($(this).attr('id'));
    $('#uploadFile_'+id_image+'').val(valor)
});



$('#password-submit-form').formValidation({
        locale: 'es_ES',
        framework: 'bootstrap',
        err: {
            container: 'tooltip'
        },
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            new_password1: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: 'Required field'
                    },
                    callback: {
                        callback: function(value, validator, $field) {
                           
                           $(".lock1").hide();
                           
                           return true;
                            
                        }
                    }
                    
                }
            },
            new_password2: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: 'Required field'
                    },
                    identical: {
                        field: 'new_password1',
                        message: 'Passwords do not match'
                    },
                    callback: {
                        callback: function(value, validator, $field) {
                           
                           $(".lock2").hide();
                           
                           return true;
                            
                        }
                    }
                    
                }
            }
        }
    });

$("#tablist a").click(function(e) {
    e.preventDefault();
    $(this).tab('show');
    console.log($(this).tab())
});

// Login and register form

$(function() {

    $('#login-form-link').click(function(e) {
        $("#login-form").delay(100).fadeIn(100);
        $("#register-form").fadeOut(100);
        $('#register-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });
    $('#register-form-link').click(function(e) {
        $("#register-form").delay(100).fadeIn(100);
        $("#login-form").fadeOut(100);
        $('#login-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });

});