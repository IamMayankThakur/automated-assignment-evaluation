var express = require('express');
var router = express.Router();
const bodyParser = require("body-parser");
const Users = require("../models/users");
const Rides = require("../models/rides");
const csv = require("csv-parser");
const fs = require("fs");
router.use(bodyParser.json());

router.route("/read")
    .post((req, res, next) => {
        var operation = req.body.operation;
        var table = req.body.table;
        if (operation == "upcoming") {
            var s = req.body.source;
            var d = req.body.destination;
            if (s.length == 0 || d.length == 0) {
                res.statusCode = 400;
                res.send();
                next();
            }
            else {
                var results = [];
                Rides.find({}).then((rides) => {
                    fs.createReadStream('AreaNameEnum.csv')
                        .pipe(csv(['Area No']))
                        .on('data', (data) => {
                            results.push(data[0]);
                        })
                        .on('end', () => {
                            if (results.includes(s) && results.includes(d)) {
                                Rides.find({ source: s, destination: d }).then((ride) => {
                                    if (ride.length == 0) {
                                        res.statusCode = 204;
                                        res.send();
                                        next();
                                    }
                                    else {
                                        var currentDate = new Date();
                                        var day = ("0" + currentDate.getDate()).slice(-2);
                                        var month = ("0" + (currentDate.getMonth() + 1)).slice(-2);
                                        var year = currentDate.getFullYear();
                                        var hours = ("0" + currentDate.getHours()).slice(-2);
                                        var minutes = ("0" + currentDate.getMinutes()).slice(-2);
                                        var seconds = ("0" + currentDate.getSeconds()).slice(-2);
                                        var output = [];
                                        var k = 0;
                                        for (var key in ride) {
                                            var d = (ride[key].timestamp).slice(0, 2);
                                            var m = (ride[key].timestamp).slice(3, 5);
                                            var y = (ride[key].timestamp).slice(6, 10);
                                            var ss = (ride[key].timestamp).slice(11, 13);
                                            var mm = (ride[key].timestamp).slice(14, 16);
                                            var hh = (ride[key].timestamp).slice(17, 19);
                                            if ((y > year) || (y == year && m > month) || (y == year && m == month && d > day) || (y == year && d == day && m == month && hh > hours) || (y == year && d == day && m == month && hh == hours && mm > minutes) || (y == year && d == day && m == month && hh == hours && mm == minutes && ss > seconds)) {
                                                output[k] = {};
                                                output[k].rideId = ride[key].rideId;
                                                output[k].username = ride[key].username;
                                                output[k].timestamp = ride[key].timestamp;
                                                k = k + 1;
                                            }
                                        }
                                        if (k == 0) {
                                            res.statusCode = 204;
                                            res.send();
                                            next();
                                        }
                                        else {
                                            res.statusCode = 200;
                                            res.send(output);
                                            next();
                                        }
                                    }
                                })
                            }
                            else {
                                res.statusCode = 400;
                                res.send();
                                next();
                            }
                        })
                })
            }


        }
        else if (operation == "display") {
            var id = req.body.rideId;
            if (id.length == 0) {
                res.statusCode = 400;
                res.send();
                next();
            }
            else {
                Rides.find({ rideId: id }).then((ride) => {
                    if (ride.length == 0) {
                        res.statusCode = 400;
                        res.send();
                        next();
                    }
                    else {
                        var output = {};
                        output.rideId = id;
                        output.created_by = ride[0].created_by;
                        output.users = ride[0].users;
                        output.timestamp = ride[0].timestamp;
                        output.source = ride[0].source;
                        output.destination = ride[0].destination;
                        res.statusCode = 200;
                        res.send(output);
                        next();
                    }
                })
            }
        }
        else {
            if (table.toLowerCase() == "users") {
                var uname = req.body.username;
                if (uname.length == 0) {
                    res.statusCode = 400;
                    res.send();
                    next();
                }
                else {
                    Users.find({ username: uname }).then(users => {
                        if (users.length == 0) {
                            res.statusCode = 400;
                            res.send();
                            next();
                        }
                        else {
                            Users.remove({ username: uname }).then(() => {
                                res.statusCode = 200;
                                res.send();
                                next();
                            });
                        }
                    });
                }
            }
            else {
                if (req.body.rideId.length == 0) {
                    res.statusCode = 400;
                    res.send();
                    next();
                }
                else {
                    Rides.find({ rideId: req.body.rideId }).then(rides => {
                        if (rides.length == 0) {
                            res.statusCode = 400;
                            res.send();
                            next();
                        }
                        else {
                            Rides.remove({ rideId: req.body.rideId }).then(() => {
                                res.statusCode = 200;
                                res.send();
                                next();
                            })
                        }
                    })
                };
            }
        }

    });

router.route("/write")
    .post((req, res, next) => {
        var operations = ["add", "join"];
        var operation = req.body.operation;
        var table = req.body.table;
        if (operation == "add") {
            if (table == "users") {
                var uname = req.body.username;
                var pwd = req.body.password;
                if (uname.length == 0 && pwd.length == 0) {
                    res.statusCode = 400;
                    res.send();
                    next();
                }
                else {
                    Users.find({ username: uname }).then((users) => {
                        if (users.length != 0 || !/^[a-fA-F0-9]{40}$/.test(pwd.toString())) {
                            res.statusCode = 400;
                            res.send();    //Username entered is not unique or pwd not in SHA 1 format
                            next();
                        }
                        else {
                            Users.create({ username: uname, password: pwd }).then((user) => {
                                res.statusCode = 201;
                                res.send();
                                next();
                            })
                        }
                    });
                }
            }
            else {
                var cb = req.body.created_by;
                var time = req.body.timestamp;
                var s = req.body.source;
                var d = req.body.destination;
                if (cb.length == 0 || time.length == 0 || s.length == 0 || d.length == 0) {
                    res.statusCode = 400;
                    res.send();
                    next();
                }
                else {
                    Users.find({ username: cb }).then((users) => {
                        if (users.length == 0) {
                            res.statusCode = 400;
                            res.send();
                            next();
                        }
                        else {
                            var results = []
                            Rides.find({}).then((rides) => {
                                fs.createReadStream('AreaNameEnum.csv')
                                    .pipe(csv(['Area No']))
                                    .on('data', (data) => {
                                        results.push(data[0]);
                                    })
                                    .on('end', () => {
                                        if ((results.includes(s) && results.includes(d))) {
                                            var Id;
                                            var us = [];
                                            if (rides.length == 0) {
                                                Id = 123;
                                            }
                                            else {
                                                var ma = 0;
                                                for (var key in rides) {
                                                    if (rides[key].rideId > ma) {
                                                        ma = rides[key].rideId;
                                                    }
                                                }
                                                Id = ma + 1;
                                            }
                                            us.push(cb);
                                            Rides.create({ created_by: cb, timestamp: time, source: s, destination: d, rideId: Id, users: us })
                                                .then((ride) => {
                                                    res.statusCode = 201;
                                                    res.send();
                                                    next();
                                                });
                                        }
                                        else {
                                            res.statusCode = 400;
                                            res.send();
                                            next();
                                        }
                                    });

                            })
                        }
                    })
                }
            }
        }
        else {
            var id = req.body.rideId;
            if (id.length == 0) {
                res.statusCode = 400;
                res.send();
                next();
            }
            else {
                Users.find({ username: req.body.username }).then((user) => {
                    if (user.length == 0) {
                        res.statusCode = 400;
                        res.send();
                        next();
                    }
                    else {
                        Rides.find({ rideId: id }).then((rides) => {
                            if (rides.length == 0) {
                                res.statusCode = 400;
                                res.send();
                                next();
                            }
                            else {
                                if ((rides[0].users).includes(req.body.username)) {
                                    res.statusCode = 204;
                                    res.send();
                                    next();
                                }
                                else {
                                    Rides.findByIdAndUpdate(rides[0]._id, { $push: { users: req.body.username } }, { 'new': true }, (err, r) => {
                                        if (err)
                                            console.log(err);
                                        res.statusCode = 200;
                                        res.send();
                                        next();
                                    })
                                }
                            }
                        })
                    }
                })
            }
        }
    });

module.exports = router;