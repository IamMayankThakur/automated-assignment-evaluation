/************************************server.js**************************************/
// Dependencies
const express = require('express');
const apiV1 = require('./routes/v1');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
require('dotenv/config');

// Initializing the server
const server = express();

// connecting to mongoDB
mongoose.connect(process.env.DB_CONNECTION,{
    useNewUrlParser: true,
    useUnifiedTopology: true,
    useCreateIndex : true,
    useFindAndModify : false
});

// configuring the server
server.use(bodyParser.urlencoded({extended: false}));
server.use(bodyParser.json());

// to handle CORS
server.use((req,res,next) => {
    res.header('Access-Control-Allow-Origin','*');
    res.header('Access-Control-Allow-Headers','Origin, X-Requested-With, Content-Type, Accept, Authorization');
    if(req.method === 'OPTIONS'){
        res.header('Acces-Control-Allow-Methods', 'POST, GET, PUT, DELETE');
        return res.status(200).json({})
    }
    next();
});

// setting the middleware to route the requests
server.use('/api/v1',apiV1);

// handling bad paths/errors
server.use((req,res,next) => {
    res.status(405).json({});
});

server.use((error, req,res,next) => {
    res.status(error.status || 500);
    res.json({});
});

// Listening on port 8080
server.listen(8080,function(){
    console.log('Listening on port 8080...');
});

/************************************v1.js***************************************/
// dependencies
const express = require('express');
const usersHandler = require('./users')
const ridesHander = require('./rides')
const dbHandler = require('./db')

// variables
const api = express();

// to route user requests
api.use('/users',usersHandler);

// to route ride requests
api.use('/rides',ridesHander);

// to route db operations
api.use('/db',dbHandler);

// to handle unknown paths and errors
api.use((req, res, next) => {
    res.status(405).json({});
})

// export
module.exports = api;

/*******************************************users.js**************************************/
// dependencies
const express = require('express');
const helper = require('../helper');
const request = require('request-promise');
require('dotenv/config');

//variables
const router = express.Router();
const serverName = process.env.SERVER;
// setting routes
// 1. Add user
router.put('/', async (req, res, next) => {
    // get the data from request body
    const username = req.body.username;
    const password = req.body.password;
    console.log('Entered put request');

    // check if password is SHA1
    if (password == null || !helper.validPass(password)) {
        console.log('Invalid password');
        res.status(400).json({});
    }
    else {
        console.log('passed password check');

        // check if user exists
        var body = {
            table: 'user',
            where: {
                username: username
            }
        };
        var options = {
            url: serverName + '/api/v1/db/read',
            body: JSON.stringify(body),
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        try {
            var response = await request.post(options);
            console.log('first response');
            response = JSON.parse(response);
            res.status(400).json({});
        } catch{
            body = {
                action: 1,
                table: 'user',
                values: [username, password]
            };
            options = {
                url: serverName + '/api/v1/db/write',
                method: 'POST',
                body: JSON.stringify(body),
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            response = await request.post(options);
            console.log('after write');
            console.log(response);
            response = JSON.parse(response);
            const statusCode = response.statusCode;

            res.status(statusCode).json({});
        }



    }


});

// 2.Remove user
router.delete('/:username', async (req, res, next) => {
    const username = req.params.username;
    console.log('in delete');
    try{
        var response = await request.post({
            url : serverName + '/api/v1/db/read',
            body : JSON.stringify({
                table : 'ride',
                action : 2,
                where : {
                    created_by : username
                }
            }), 
            headers: {
                'Content-Type': 'application/json'
            }
        });
        response = JSON.parse(response);
        console.log(response);
        if(response.length > 0){
            console.log('sending response');
            res.status(400).json({});
            return;
        }
    }catch(err){
        console.log(err);
    }
    

    var body = {
        table: 'user',
        action : 2,
        where: {
            username: username
        }
    };
    var options = {
        url: serverName + '/api/v1/db/write',
        body: JSON.stringify(body),
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try{
        var response = JSON.parse(await request.post(options));
        console.log('delete response');
        console.log(response);
        res.status(response.statusCode).json({});
    } catch(error){
        console.log(error);
        res.status(400).json({});
    }
});

router.use((req,res,next) => {
    res.status(405).json({});
});

// export the router
module.exports = router

/*****************************************rides.js****************************************/
// dependencies
const express = require('express');
const request = require('request-promise');
const areas = require("../constants");
const helper = require("../helper");
require('dotenv/config');

//variables
const router = express.Router();
const serverName = process.env.SERVER;

// setting routes
// 3. Create new ride
router.post('/', async (req, res, next) => {
    // getting the request body
    const username = req.body.created_by;
    const timeStamp = helper.extractDate(req.body.timestamp);
    const source = Number(req.body.source);
    const destination = Number(req.body.destination);
    if (areas[source] == undefined || areas[destination] == undefined || areas[source] == areas[destination] || helper.isInvalid(timeStamp)) {
        res.status(400).json({});
        return;
    }
    console.log('timestamp:');
    console.log(timeStamp);
    // TODO validate
    var body = {
        table: 'user',
        where: {
            username: username
        }
    };

    var options = {
        url: serverName + '/api/v1/db/read',
        body: JSON.stringify(body),
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try {
        console.log('Checking for user detail');
        var response = await request.post(options);
    } catch (err) {
        console.log('Inside rides.js');
        console.log(err);
        res.status(400).json({});
        return;
    }

    body = {
        action: 1,
        table: "ride",
        values: [username, timeStamp, source, destination, []]
    };
    options = {
        url: serverName + '/api/v1/db/write',
        body: JSON.stringify(body),
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    try {
        console.log('Writing ride details');
        var response = JSON.parse(await request.post(options));
        console.log('Write complete');
        console.log(response);
        const statusCode = response.statusCode;
        console.log('sending response');
        res.status(statusCode).json({});
    } catch{
        res.status(400).json({});
    }
});

// 4. List all upcoming rides for given source and destination
router.get('/', async (req, res, next) => {
    console.log('Get called');
    const source = Number(req.query.source);
    const destination = Number(req.query.destination);
    const currentDate = new Date();
    if (areas[source] == undefined || areas[destination] == undefined || areas[source] == areas[destination]) {
        res.status(400).json({});
        return;
    }
    const body = {
        action : 4,
        table: 'ride',
        where: {
            source: source,
            destination: destination,
            timestamp : {
                '$gte' : currentDate
            }
        }
    };
    const options = {
        url: serverName + '/api/v1/db/read',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json'
        }
    };
    try {
        var response = JSON.parse(await request.post(options));
        console.log('Inside get ride');
        console.log(response);
        if (response.length != 0) {
            response = helper.formatResponse(response);
            res.status(200).json(response);
        } else {
            res.status(204).json({});
        }

    } catch (err) {
        console.log(err);
        res.status(400).json({});
    }
});

// 5. List all details for given ride
router.get('/:rideId', async (req, res, next) => {
    const rideId = req.params.rideId;
    var body = {
        action : 5,
        table: 'ride',
        where: {
            rideId: rideId
        }
    };
    var options = {
        url: serverName + '/api/v1/db/read',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json'
        }
    };
    try{
        var response = JSON.parse(await request.post(options));
        if(Object.keys(response).length == 0){
            res.status(400).json({});
        } else{
            console.log(response.timestamp);
            response.timestamp = helper.formatDate(response.timestamp);
            res.status(200).json(response);
        }
    } catch(err){
        console.log(err);
        res.status(400).json({});
    }

});

// 6. Join existing ride
router.post('/:rideId', async (req, res, next) => {
    // get request body
    console.log('request sent');
    console.log(req.body);
    const username = req.body.username;
    const rideId = req.params.rideId;
    const currentDate = new Date();
    console.log('username from req');
    console.log(username);

    var body = {
        action : 4,
        table : 'ride',
        where : {
            rideId : rideId,
            timestamp : {
                '$gte' : currentDate
            },
            created_by : {
                '$ne' : username
            }
        }
    };
    var options = {
        url: serverName + '/api/v1/db/read',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json'
        }
    }
    try{
        var response = JSON.parse(await request.post(options));
        console.log('After checks in joining');
        console.log(response);
        if(response.length == 0 || response.statusCode === 400){
            res.status(400).json({});
            return;
        }
        body = {
            table : 'user',
            where : {
                username : username
            }
        };
        console.log('Inside first try');
        console.log(body);
        options.body = JSON.stringify(body);
        response = JSON.parse(await request.post(options));
        const statusCode = response.statusCode;
        if(statusCode != 200){
            res.status(400).json({});
            return;
        }
    } catch(err){
        console.log(err);
        res.status(400).json({});
        return;
    }

    body = {
        action : 6,
        table : 'ride',
        users : username,
        where : {
            rideId : rideId
        }
    };
    console.log('sending to ride');
    console.log(body);
    options.url = serverName + '/api/v1/db/write';
    options.body = JSON.stringify(body);

    try{
        var response = JSON.parse(await request.post(options));
        const statusCode = response.statusCode;
        res.status(statusCode).json({});

    } catch(err){
        console.log(err);
        res.status(400).json({});
    }

});

// 7. Delete a ride
router.delete('/:rideId', async (req, res, next) => {
    const rideId = req.params.rideId;

    var body = {
        table: 'ride',
        action : 2,
        where: {
            rideId: rideId
        }
    };
    var options = {
        url: serverName + '/api/v1/db/write',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try{
        var response = JSON.parse(await request.post(options));
        console.log('delete response');
        console.log(response);
        res.status(response.statusCode).json({});
    } catch(error){
        next(error);
    }
});

router.use((req,res,next) => {
    res.status(405).json({});
});

// export the router
module.exports = router

/*************************************db.js***********************************************/

// dependencies
const express = require('express');
const User = require('../models/user');
const Ride = require('../models/ride');

// variables
const router = express.Router();

// 8. Write to db
router.post('/write', async (req, res, next) => {
    /*console.log('db/write called');
    res.status(200).json({
        something : 'something'
    });*/
    const action = req.body.action;
    const table = req.body.table;

    // if action is 1 create
    if (action == 1) {
        if (table === 'user') {
            const user = new User({
                username: req.body.values[0],
                password: req.body.values[1],
                rides: req.body.values[2]
            });
            console.log(user);
            try {
                const savedUser = await user.save();
                console.log(savedUser);
                res.json({
                    statusCode: 201
                });
            } catch (err) {
                console.log('Inside db');
                console.log(err);
                res.json({
                    statusCode: 500
                });
            }

        }
        if (table === 'ride') {
            const ride = new Ride({
                created_by: req.body.values[0],
                timestamp: req.body.values[1],
                source: req.body.values[2],
                destination: req.body.values[3],
                users: req.body.values[4]
            });
            try {
                console.log('Saving ride details');
                const savedRide = await ride.save();
                console.log(savedRide);
                res.json({
                    statusCode: 201
                });
            } catch (err) {
                console.log('Inside ride of db');
                console.log(err);
                res.json({
                    statusCode : 500
                });
            }
        }
    } else if (action == 2) {
        if (table === 'user') {
            try {
                const username = req.body.where.username;
                var response = await Ride.updateMany({users : username}, {$pull : {users : username}});
                console.log('Update response');
                console.log(response);
                response = await User.deleteOne(req.body.where);
                console.log('delete response');
                console.log(response); 
                if(response.deletedCount > 0){
                    res.status(200).json({
                        statusCode : 200
                    });
                }  else{
                    res.status(200).json({
                        statusCode : 400
                    });
                }             
                
            } catch (err) {
                console.log('Inside action 2 user db');
                console.log(err);
                res.status(400).json({
                    statusCode : 400
                });
            }
        } else if(table == 'ride')
        {
            try {
                const response = await Ride.deleteOne(req.body.where);
                console.log(response);
                if(response.deletedCount > 0){
                    res.status(200).json({
                        statusCode : 200
                    });
                }  else{
                    res.status(200).json({
                        statusCode : 400
                    });
                } 
            } catch (err) {
                console.log('Inside action 2 user db');
                console.log(err);
                res.status(400).json({
                    statusCode : 400
                });
            }
        }
    } else if(action == 6){
        if(table == 'ride'){
            try{
                const response = await Ride.updateOne(req.body.where,{ $addToSet : {users : req.body.users}});
                console.log(response);
                if(response.nModified == 0){
                    res.json({
                        statusCode : 400
                    });
                }else{
                    res.status(200).json({
                        statusCode : 200
                    });
                }                
            } catch(err){
                console.log(err);
                res.status(400).json({
                    statusCode : 400
                });
            }
        }
    }
});

// 9. Read from db
router.post('/read', async (req, res, next) => {

    const table = req.body.table;
    const action = req.body.action;
    

    if (table === "user") {
        console.log('Reading db');
        try {
            var result = await User.findOne(req.body.where);
            console.log(result);
            console.log(result.username);
            res.status(200).json({
                statusCode: 200
            });
        } catch (err) {
            console.log('Inside db');
            console.log(err);
            res.status(400).json({
                statusCode : 400
            });
        }
    } else if (table == 'ride') {
        const action = req.body.action;
        console.log('Ride db read');
        var result;
        try {
            if(action == 2){
                result = await Ride.find(req.body.where);
            }
            if(action == 4){
                result = await Ride.find(req.body.where).select('rideId created_by timestamp -_id');
            }
            if(action == 5){
                result = await Ride.findOne(req.body.where).select('-_id -__v');
            }            
            console.log(result);
            res.status(200).json(result);
        } catch (err) {
            console.log(err);
            res.status(200).json({
                statusCode : 400
            });
        }
    }

});

router.use((req,res,next) => {
    res.status(405).json({});
});

//
module.exports = router;


