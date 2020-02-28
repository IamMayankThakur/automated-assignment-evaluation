const User = require('../../models/User');
const Ride = require('../../models/Ride');

var rp = require('request-promise-native');

function checkDate(date){
    var pattern = new RegExp("^(3[01]|[12][0-9]|0[1-9])-(1[0-2]|0[1-9])-[0-9]{4}:([0-5]?[0-9])-([0-5]?[0-9])-(2[0-3]|[01]?[0-9])$");
    if (date.search(pattern)===0) return true;
    else return false;
}
  
function convertToISO(date){
    var cleanDate = date.replace(/-/g, " ");
    cleanDate = cleanDate.replace(/:/g, " ");
    var splitDate = cleanDate.split(" "); 
    var final = splitDate[2]+"-"+splitDate[1]+"-"+splitDate[0]+"T"+splitDate[5]+":"+splitDate[4]+":"+splitDate[3]+"Z";
    return final;
}  

function convertToFormat(date){
    var cleanDate = date.replace("T", "-");
    cleanDate = cleanDate.replace("Z", "");
    cleanDate = cleanDate.replace(/:/g, "-");
    var splitDate = cleanDate.split("-");
    var final = splitDate[2]+"-"+splitDate[1]+"-"+splitDate[0]+":"+(parseInt(splitDate[5]).toString())+"-"+splitDate[4]+"-"+splitDate[3];
    return final;
}

module.exports = (app) => {
    app.post("api/v1/db/read", (req, res) => {
        var model = req.body.model;
        var parameters = req.body.parameters;

        if (model && parameters) {
          let Model = null;
          const params = parameters;
          if (model == "User") {
            Model = User;
          } else if (model == "Ride") {
            Model = Ride;
          }
            Model.find(
                params,
                (err, results) => {
                    if(err){
                        console.log(err.message);
                        return res.status(500).send({
                            success: false,
                            message: "Error: Server error.",
                            error: err.message,
                        });
                    }
                    if(results.length == 0){
                        return res.status(204).send({
                            success: false,
                            message: 'Error: Data not found.'
                        });
                    }
                    return res.status(200).send({
                        success: true,
                        data: results
                    })
            });        
        }
        else {
            return res.status(400).send({
                success: false,
                message: 'Error: Model and parameters cannot be blank.'
            });      
        } 
      });
      
      app.post("api/v1/db/write", (req, res) => {
        var model = req.body.model;
        var operation = req.body.operation;
        var parameters = req.body.parameters;
        var query = req.body.query;

        if (model && operation) {
            if(!parameters){
                return res.status(400).send({
                    success: false,
                    message: 'Error: Parameters cannot be blank.'
                });
            }
            if(operation == "update" && !query){
                return res.status(400).send({
                    success: false,
                    message: 'Error: Query cannot be blank.'
                });
            }

            let Model = null;
            if (model == "User") {
            Model = User;
            } else if (model == "Ride") {
            Model = Ride;
            }
        
            try {
            switch (operation) {
                case "insert":
                    const user = new Model(parameters);
                    user.save();
                    break;
                case "delete":
                    Model.findOneAndDelete(parameters);
                    break;
                case "update":
                    Model.findOneAndUpdate(req.body.query, parameters);
                    break;
            }
            console.log("DB write done.");
                return res.status(200).send({
                    success: true,
                    message: 'DB write done.'
                });
            } catch (err) {
                return res.status(500).send({
                    success: false,
                    message: 'Error: Server error.'
                });
            }
        }
        else {
            return res.status(400).send({
                success: false,
                message: 'Error: Model and operation cannot be blank.'
            });      
        } 
      });


  // API: 1
  app.put('/api/v1/users', (req, res) => {
    var username = req.body.username;
    var password = req.body.password;
    if (!username) {
        return res.status(400).send({
            success: false,
            message: 'Error: username cannot be blank.'
        });
    }
    if (!password) {
        return res.status(400).send({
            success: false,
            message: 'Error: password cannot be blank.'
        });
    }
    if (password.length != 40) {
        return res.status(400).send({
            success: false,
            message: 'Error: password is not 40 chars long.'
        });
    }

    rp.post("http://localhost:8080/api/v1/db/read", {
        json: {
            model: "User",
            parameters: { username: username },
        }
    }).then((body) => {
        if(body.status == 200){
            var previousUsers = body.body;
            if (previousUsers.length > 0) {
                return res.status(400).send({
                    success: false,
                    message: 'Error: User already exists.'
                });
            }
            // Save the new user
            var newUser = {
                "username": username,
                "password": password
            };
    
            rp.post("http://localhost:8080/api/v1/db/write", {
                json: {
                    model: "User",
                    parameters: newUser,
                    operation: "insert"
                }
            }).then((body) => {
                if(body.status == 200){
                    return res.status(201).send({});
                }
            }).catch((err) => {
                return res.status(500).send({
                    success: false,
                    message: 'Error: Server error.',
                    error: err.message
                });
            });
        }
    }).catch((err) => {
        return res.status(500).send({
            success: false,
            message: 'Error: Server error.',
            error: err.message
        });
    });

  });

  // API: 2
  app.delete('/api/v1/users/:username', function (req, res) {
    var username = req.params.username;
    if (!username) {
        return res.status(400).send({
            success: false,
            message: "Error: username not recieved."
        });
    }

    rp.post("http://localhost:8080/api/v1/db/write", {
      json: {
          model: "User",
          parameters: { username: username },
          operation: "delete"
      }
      }).then((body) => {
          if(body.status == 200){
              return res.status(200).send({});
          }
      }).catch((err) => {
          return res.status(500).send({
              success: false,
              message: 'Error: Server error.',
              error: err.message
          });
      });
    });

  //API:3 Create a new ride
  app.post('/api/v1/rides', (req, res) => {
    var created_by = req.body.created_by;
    var timestamp = req.body.timestamp;
    var source = parseInt(req.body.source);
    var destination = parseInt(req.body.destination);

    if (!created_by) {
        return res.status(400).send({
            success: false,
            message: 'Error: created_by cannot be blank.'
        });
    }
    if (!source) {
        return res.status(400).send({
            success: false,
            message: 'Error: source cannot be blank.'
        });
    }
    if (!destination) {
        return res.status(400).send({
            success: false,
            message: 'Error: destination cannot be blank.'
        });
    }

    if (destination < 1 || destination > 198) {
      return res.status(400).send({
          success: false,
          message: 'Error: destination out of range.'
      });
    }

    // Find to check if user is valid
    User.find({
        username: created_by
    }, (err, previousUsers) => {
        if (err) {
            console.log(err.message);
            return res.status(500).send({
              success: false,
              message: "Error: Server error.",
              error: err.message,
            });
        } if (previousUsers.length == 0) {
            return res.status(400).send({
                success: false,
                message: 'Error: User does not exist.'
            });
        }
        const newRide = new Ride();

        if(timestamp){
            if(checkDate(timestamp) == true){
              var returnedDate = convertToISO(timestamp);
              var dateObject = new Date(returnedDate);
              var todaysDate = new Date();

              var adjustedDate = new Date(todaysDate.getTime() + 60000);

              if(dateObject<adjustedDate){
                return res.status(400).send({
                  success: false,
                  message: 'Error: Timestamp is before now.'
                });
              }

              newRide.timestamp = new Date(returnedDate);
            }
            else{
              return res.status(400).send({
                success: false,
                message: 'Error: Timestamp not in correct format.'
              });
            }
        }
  

        rp.post("http://localhost:8080/api/v1/db/read", {
          json: {
              model: "Area",
              parameters: { areano: source },
          }
        }).then((body) => {}).catch((err) => {
          return res.status(500).send({
            success: false,
            message: 'Error: Server find error.'
          });
        });

        rp.post("http://localhost:8080/api/v1/db/read", {
          json: {
              model: "Area",
              parameters: { areano: destination },
          }
        }).then((body) => {}).catch((err) => {
          return res.status(500).send({
            success: false,
            message: 'Error: Server find error.'
          });
        });

        var newRide = {
            "created_by": created_by,
            "source": source,
            "destination": destination,
            "created_by": created_by
        };

        rp.post("http://localhost:8080/api/v1/db/write", {
            json: {
                model: "Ride",
                parameters: newRide,
                operation: "insert"
            }
        }).then((body) => {
            if(body.status == 200){
                return res.status(201).send({});
            }
        }).catch((err) => {
            return res.status(500).send({
                success: false,
                message: 'Error: Server error.',
                error: err.message
            });
        });
    });
  });



  // API: 4 List all upcoming rides for a given source and destination
  app.get('/api/v1/rides/', (req, res) => {
    var source = req.query.source;
    var destination = req.query.destination;

    var retRides = [];

    if (!source) {
      return res.status(400).send({
        success: false,
        message: 'Error: source parameter cannot be blank.'
      });
    }
    if (!destination) {
        return res.status(400).send({
          success: false,
          message: 'Error: destination parameter cannot be blank.'
        });
    }

    rp.post("http://localhost:8080/api/v1/db/read", {
      json: {
          model: "Ride",
          parameters: {
            source : source,
            destination : destination,
            timestamp : { $gte : new Date() }
          },
      }
      }).then((body) => {
        if(body.status == 200){

        var formatedDate;

        for(var i = 0; i < rides.length; i++){
          formatedDate = convertToFormat(rides[i].timestamp.toISOString());
          retRides.push({
            "rideID":rides[i]._id,
            "created_by":rides[i].created_by,
            "timestamp":formatedDate
          });
        }

        return res.status(200).send(retRides);
      }
      }).catch((err) => {
        console.log(err.message);
            return res.status(500).send({
                success: false,
                message: "Error: Server error.",
                error: err.message,
        });
      });
  });

  // API: 5 List all the details of a given ride
  app.get('/api/v1/rides/:rideID', (req, res) => {
    var rideID = req.params.rideID;

    if (!rideID) {
      return res.status(400).send({
        success: false,
        message: 'Error: rideID parameter cannot be blank.'
      });
    }

    rp.post("http://localhost:8080/api/v1/db/read", {
      json: {
          model: "Ride",
          parameters: {
            _id : rideID,
          },
      }
      }).then((body) => {
        if(body.status == 200){

          var formatedDate = convertToFormat(ride[0].timestamp.toISOString());

          var rideStruct = {
            "rideID": ride[0]._id,
            "created_by": ride[0].created_by,
            "users": ride[0].users,
            "timestamp": formatedDate,
            "source": ride[0].source,
            "destination": ride[0].destination
          }
    
          return res.status(200).send(rideStruct);
      }
      }).catch((err) => {
        console.log(err.message);
            return res.status(500).send({
                success: false,
                message: "Error: Server error.",
                error: err.message,
        });
      });
  });


  //API:6 Join an existing ride
  app.post('/api/v1/rides/:rideID', (req, res) => {

    var rideID = req.params.rideID;
    var username = req.body.username;

    if (!rideID) {
      return res.status(400).send({
        success: false,
        message: 'Error: rideID not provided.'
      });
    }

      
    rp.post("http://localhost:8080/api/v1/db/write", {
      json: {
          model: "Ride",
          query: { _id: rideID },
          parameters: {
            $addToSet: { users : username }
        },
          operation: "update"
      }
      }).then((body) => {
          if(body.status == 200){
              return res.status(201).send({});
          }
      }).catch((err) => {
          return res.status(500).send({
              success: false,
              message: 'Error: Server error.',
              error: err.message
          });
      });


    User.find({
      username: username,
    }, (err, user) => {
      if (err) {
        console.log(err.message);
        return res.status(500).send({
          success: false,
          message: "Error: Server error.",
          error: err.message
        });
      }
      if (user.length == 0) {
        return res.status(400).send({
          success: false,
          message: 'Error: User does not exist.'
        });
      }
    })
  }),

  //API: 7 Delete a ride
  app.delete('/api/v1/rides/:rideID', (req, res) => {
    var rideID = req.params.rideID;
    if (!rideID) {
        return res.status(405).send({
            success: false,
            message: "Error: rideID not recieved."
        });
    }

    rp.post("http://localhost:8080/api/v1/db/write", {
      json: {
          model: "Ride",
          parameters: { _id: rideID },
          operation: "delete"
      }
      }).then((body) => {
          if(body.status == 200){
              return res.status(200).send({});
          }
      }).catch((err) => {
          return res.status(500).send({
              success: false,
              message: 'Error: Server error.',
              error: err.message
          });
      });
  });
};

