const express = require('express');
const connectDB = require('./config/db');

// Express
const app = express();

// Connect database
connectDB();

// Init middleware
app.use(express.json({ extended: false }));

app.use('/api/v1/rides', require('./routes/rides'));
app.use('/api/v1/users', require('./routes/users'));
app.use('/api/v1/db', require('./routes/db_utils'));

app.use((err, req, res, next) => {
    if (err && err.error && err.error.isJoi) {
        res.status(400).send();
    } else {
        next(err);
    }
});

const PORT = process.env.PORT || 8000;

app.listen(PORT, () => console.log(`Listening on port ${PORT}`));



//  ==========================================
//              users.js
//  ==========================================

const express = require('express');
const router = express.Router();
const request = require('request-promise');
const Joi = require('@hapi/joi');
const validator = require('express-joi-validation').createValidator({
    passError: true
});
const { checkUserExists, checkRideExists } = require('../utils/check');

// ROUTE: /api/v1/users

/*     API 1: Add user
 *
 *      Request: ​{
 *          “username”: “userName”,
 *
 *          “password”: “3d725109c7e7c0bfb9d709836735b56d943d263f”
 *      }
 *
 *      Response: {}
 *
 */
const createUserSchema = Joi.object().keys({
    username: Joi.string().required(),
    password: Joi.string()
        .hex()
        .min(40)
        .max(40)
        .required()
});

router.put('/', validator.body(createUserSchema), async (req, res) => {
    const { username, password } = req.body;

    try {
        if (await checkUserExists('username', { username })) {
            return res.status(400).send();
        } else {
            const options = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/write',
                json: true,
                body: {
                    flag: 1,
                    table: 'Users',
                    fields: {
                        username,
                        password
                    }
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };

            const result = await request(options);
            return res.status(201).send();
        }
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

/*     API 2: Remove user
 *
 *      Request: ​{}
 *
 *      Response: ​{}
 *
 */

router.delete('/:username', async (req, res) => {
    const username = req.params.username;

    try {
        if (await checkUserExists('username', { username })) {
            const options = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/write',
                json: true,
                body: {
                    flag: 0,
                    table: 'Users',
                    fields: {
                        username
                    }
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };

            await request(options);

            return res.status(200).send();
        } else {
            return res.status(400).send();
        }
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

// Error 405 for API 1 and API 2
router.all('/', (req, res) => {
    return res.status(405).send();
});

module.exports = router;



//  ==========================================
//              rides.js
//  ==========================================

const express = require('express');
const router = express.Router();
const Joi = require('@hapi/joi').extend(require('@hapi/joi-date'));
const validator = require('express-joi-validation').createValidator({
    passError: true
});
const { checkUserExists, checkRideExists } = require('../utils/check');
const request = require('request-promise');
const config = require('config');
const areaMin = config.get('areaMin');
const areaMax = config.get('areaMax');
const date = require('date-and-time');

// ROUTE: /api/v1/rides

/**     API 3: Create a new ride
 *
 *      Route: ​/api/v1/rides
 *      Request: ​{
 *          “created_by” : “{username}”,              // username of the user who is creating the ride
 *          “timestamp“ : “DD-MM-YYYY:SS-MM-HH”,     // Timestamp of the ride start time
 *          “source” : “{source}”,                  // Source of the ride
 *          “destination” : “{destination}”        // Destination of the ride
 *       }
 *      Response: ​{}
 *
 */

const createRideSchema = Joi.object({
    created_by: Joi.string().required(),
    timestamp: Joi.date()
        .format('DD-MM-YYYY:ss-mm-HH')
        .required(),
    source: Joi.number()
        .integer()
        .min(areaMin)
        .max(areaMax)
        .required(),
    destination: Joi.number()
        .integer()
        .min(areaMin)
        .max(areaMax)
        .disallow(Joi.ref('source'))
        .required()
});

router.post('/', async (req, res) => {
    const { value, error } = createRideSchema.validate(req.body);
    // console.log(value);

    // check if username exists

    try {
        const { created_by: username } = value;
        if (!error && (await checkUserExists('username', { username }))) {
            let ride = value;
            ride.timestamp = req.body.timestamp;
            ride.users = [];

            const options = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/write',
                json: true,
                body: {
                    flag: 1,
                    table: 'Rides',
                    fields: ride
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };

            const response = await request(options);

            return res.status(201).send();
        }

        // validation error or username doesn't exist
        return res.status(400).send();
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

/**     API 4: List all upcoming rides for a given source and destination
 *
 *      Route: ​/api/v1/rides?source={source}&destination={destination}
 *      Request: ​{}
 *      Response: ​[
 *          {
 *              “rideId“: 1234,                     // unique unsigned number
 *               “username“: “{username}”,           // username of the user who created the ride
 *               “timestamp“: “DD-MM-YYYY:SS-MM-HH”  // timestamp of the ride start time
 *          },
 *          {
 *          ...
 *           },
 *      ]
 *
 */

const listRidesSchema = Joi.object({
    source: Joi.number()
        .integer()
        .min(areaMin)
        .max(areaMax)
        .required(),
    destination: Joi.number()
        .integer()
        .min(areaMin)
        .max(areaMax)
        .disallow(Joi.ref('source'))
        .required()
});

router.get('/', validator.query(listRidesSchema), async (req, res) => {
    const { source, destination } = req.query;

    const options = {
        method: 'POST',
        uri: 'http://localhost:8000/api/v1/db/read',
        json: true,
        body: {
            table: 'Rides',
            fields: 'rideId created_by timestamp',
            condition: {
                source,
                destination
            }
        },
        headers: {
            'Content-type': 'application/json'
        }
    };

    try {
        let ride_list = await request(options);
        // console.log(ride_list);

        if (ride_list.length > 0) {
            const date_format = date.compile('DD-MM-YYYY:ss-mm-HH');

            // selecting upcoming rides and changing them to required format
            ride_list = ride_list
                .filter(
                    ride => date.parse(ride.timestamp, date_format) > new Date()
                )
                .map(ride => {
                    return {
                        rideId: ride.rideId,
                        username: ride.created_by,
                        timestamp: ride.timestamp
                    };
                });
        }

        if (ride_list.length === 0) {
            return res.status(204).send();
        }

        return res.status(200).send(ride_list);
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

/*     Error 405 for API 3 and API 4
 */
router.all('/', (req, res) => {
    return res.status(405).send();
});

/*     API 5: List all the details of a given ride
 *
 *      Request: ​{}
 *      Response: ​{
 *          “rideId” : “{rideId}”,                                 // Globally unique rideId
 *          “created_by” : “{username}”,                          // username of the user who created the ride
 *          “users” : [“{username1}”, “{username1}”, ..],        // Username of all the users associated with the ride
 *          “timestamp“ : “DD-MM-YYYY:SS-MM-HH”,                // Timestamp of the ride start time
 *          “source” : “{source}”,
 *          “destination” : “{destination}”
 *      }
 *
 */

const listRideSchema = Joi.object({
    rideId: Joi.number()
        .integer()
        .required()
});

router.get('/:rideId', validator.params(listRideSchema), async (req, res) => {
    const { rideId } = req.params;

    try {
        if (await checkRideExists('rideId', { rideId })) {
            const options = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/read',
                json: true,
                body: {
                    table: 'Rides',
                    fields:
                        'rideId created_by users timestamp source destination',
                    condition: {
                        rideId
                    }
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };

            const ride_list = await request(options);
            return res.status(200).send(ride_list[0]);
        }
        // rideId doesn't exist
        return res.status(400).send();
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

/*     API 6: Join an existing ride
 *
 *      Request: ​{
 *          “username” : “{username}”       // Username of the user who is trying to join the ride
 *      }
 *      Response: ​{}
 *
 */

const joinRidesSchema = Joi.object().keys({
    username: Joi.string().required()
});

router.post('/:rideId', validator.body(joinRidesSchema), async (req, res) => {
    const rideId = req.params.rideId;
    const { username } = req.body;

    try {
        if (
            (await checkRideExists('rideId', { rideId })) &&
            (await checkUserExists('username', { username }))
        ) {
            const getUsersArrayOptions = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/read',
                json: true,
                body: {
                    table: 'Rides',
                    fields: 'created_by users',
                    condition: {
                        rideId
                    }
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };
            const usersArray = await request(getUsersArrayOptions);

            if (
                usersArray[0].users.includes(username) ||
                usersArray[0].created_by == username
            ) {
                return res.status(400).send();
            }

            usersArray[0].users.push(username);
            const users = usersArray[0].users;

            const joinRideOptions = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/write',
                json: true,
                body: {
                    flag: 1,
                    table: 'Rides',
                    fields: {
                        rideId,
                        users
                    }
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };

            await request(joinRideOptions);

            return res.status(200).send();
        } else {
            return res.status(400).send();
        }
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

/*     API 7: Delete a ride
 *
 *      Request: ​{}
 *      Response: ​{}
 *
 */
router.delete('/:rideId', async (req, res) => {
    const rideId = req.params.rideId;

    try {
        if (await checkRideExists('rideId', { rideId })) {
            const options = {
                method: 'POST',
                uri: 'http://localhost:8000/api/v1/db/write',
                json: true,
                body: {
                    flag: 0,
                    table: 'Rides',
                    fields: {
                        rideId
                    }
                },
                headers: {
                    'Content-type': 'application/json'
                }
            };

            await request(options);

            return res.status(200).send();
        } else {
            return res.status(400).send();
        }
    } catch (error) {
        console.error(error.message);
        return res.status(500).send();
    }
});

/*     Error 405 for API 5, API 6 and API 7
 */
router.all('/:rideId', (req, res) => {
    return res.status(405).send();
});

module.exports = router;
