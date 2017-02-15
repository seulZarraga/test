/**
 * Created by Agustino on 08/09/16.
 */

$(function () {

    $('#login-form').formValidation({
        framework: 'bootstrap',
        fields: {
            email: {
                validators: {
                    notEmpty: {
                        enabled: true
                    },
                    emailAddress: {
                        enabled: true
                    }
                }
            },
            password:{
                validators: {
                    notEmpty: {
                        enabled: true
                    },
                    stringLength: {
                        min: 8
                    }
                }
            }
        }
    });

    $('#register-form').formValidation({
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
            password: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: 'Campo obligatorio.'
                    },
                    stringLength: {
                        min: 8
                    },
                    callback: {
                        callback: function(value, validator, $field) {
                           
                           $(".lock1").hide();
                           
                           return true;
                            
                        }
                    }
                    
                }
            },
            password_confirmation: {
                validators: {
                    notEmpty: {
                        enabled: true,
                        message: 'Campo obligatorio.'
                    },
                    stringLength: {
                        min: 8
                    },
                    identical: {
                        field: 'password',
                        message: 'Las contraseñas no coinciden.'
                    },
                    callback: {
                        callback: function(value, validator, $field) {
                           
                           $(".lock2").hide();
                           
                           return true;
                            
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
            nombre_empresa: {
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


});