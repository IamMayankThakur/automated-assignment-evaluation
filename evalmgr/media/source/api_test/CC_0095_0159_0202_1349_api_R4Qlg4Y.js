// @route PUT /api/v1/users
// @desc add a new user
router.all("/", async (req, res) => {
  // Check if correct HTTP method is used
  if (req.method === "PUT") {
    if (joiSchemas.joiValidate(joiSchemas.createUser, req.body)) {
      try {
        // Check if user already exist
        // Make read db call
        let user = await rp.post(config.get("DB_API_URI").READ, {
          json: {
            model: "User",
            parameters: {
              username: req.body.username
            }
          }
        });

        console.log(user);
        if (user.length != 0) {
          return res.status(400).json({ msg: "1" });
        }

        await rp.post(config.get("DB_API_URI").WRITE, {
          json: {
            model: "User",
            parameters: {
              username: req.body.username,
              password: req.body.password
            },
            op: "in"
          }
        });

        return res.status(201).json({});
      } catch (error) {
        console.log(error.message);
        return res.status(500).json({ msg: "Error occured" });
      }
    } else {
      //  remember to change
      return res.status(400).json({ msg: "2" });
    }
  } else {
    return res.status(405).json({});
  }
});

// @route DELETE /api/v1/users/:username
// @desc Remove a user
router.all("/:username", async (req, res) => {
  if (req.method == "DELETE") {
    // Check if the user exist or not
    let user = await rp.post(config.get("DB_API_URI").READ, {
      json: {
        model: "User",
        parameters: {
          username: req.params.username
        }
      }
    });

    if (user.length == 0) {
      return res.status(400).json({ msg: "1" });
    }

    await rp.post(config.get("DB_API_URI").WRITE, {
      json: {
        model: "User",
        parameters: {
          username: req.params.username
        },
        op: "del"
      }
    });

    return res.status(200).json({});
  } else {
    return res.status(405).json({});
  }
});

// generate a random number
const getRandomInt = max => {
  max = max || Number.MAX_SAFE_INTEGER;
  return Math.floor(Math.random() * Math.floor(max));
};

// Check if user exists
const userExists = async parameters => {
  let user = await rp.post(config.get("DB_API_URI").READ, {
    json: {
      model: "User",
      parameters: parameters
    }
  });

  if (user.length != 0) return true;
  return false;
};

// Check if ride exists
const rideExists = async parameters => {
  const rides = await rp.post(config.get("DB_API_URI").READ, {
    json: {
      model: "Ride",
      parameters: parameters
    }
  });

  if (rides.length != 0) return true;
  return false;
};

// Compare timestamp with time when request is made
const compareTime = (timestamp, d) => {
  const dateTime = timestamp.split(":");

  // console.log(dateTime);

  let date = dateTime[0].split("-");
  let time = dateTime[1].split("-");

  // console.log(date, time);
  date = date.map(num => {
    return parseInt(num, 10);
  });
  time = time.map(num => {
    return parseInt(num, 10);
  });

  const curr = new Date(
    date[2],
    date[1] - 1,
    date[0],
    time[2],
    time[1],
    time[0]
  );

  if (d.getTime() < curr.getTime()) {
    return 1;
  }
  return 0;
};

router
  .route("/")
  .post(async (req, res) => {
    if (
      !joiSchemas.joiValidate(joiSchemas.createRide, req.body) ||
      req.body.source == req.body.destination
    ) {
      return badRequest("Invalid params", req, res);
    }

    const created_by = req.body.created_by;
    const timestamp = req.body.timestamp;
    const source = req.body.source;
    const destination = req.body.destination;

    let isValidRideId = false;
    let rideId = 0;

    try {
      if (!(await userExists({ username: created_by }))) {
        return badRequest("Bad params", req, res);
      }
      do {
        rideId = getRandomInt();
        if (!(await rideExists({ rideId }))) {
          isValidRideId = true;
        }
      } while (!isValidRideId);

      let newRide = Object.assign(
        {},
        {
          created_by,
          timestamp,
          source,
          destination,
          rideId
        }
      );

      await rp.post(config.get("DB_API_URI").WRITE, {
        json: {
          model: "Ride",
          parameters: newRide,
          op: "in"
        }
      });

      return res.status(201).json({});
    } catch (error) {
      console.log(error.message);
      return res.status(500).json({ msg: "Server Error", error });
    }
  })
  .get(async (req, res) => {
    if (joiSchemas.joiValidate(joiSchemas.getRideSrcDst, req.query)) {
      const source = req.query.source;
      const destination = req.query.destination;
      // Get all rides with given source and dest
      try {
        let rides = await rp.post(config.get("DB_API_URI").READ, {
          json: {
            model: "Ride",
            parameters: {
              source: source,
              destination: destination
            }
          }
        });

        const d = new Date();

        const validRides = [];
        for (var i = 0; i < rides.length; i++) {
          if (compareTime(rides[i].timestamp, d)) {
            validRides.push({
              rideId: rides[i].rideId,
              username: rides[i].created_by,
              timestamp: rides[i].timestamp
            });
          }
        }

        if (validRides.length == 0) {
          return res.status(204).json({ msg: "Ride does not exist" });
        }

        return res.status(200).send(validRides);
      } catch (error) {
        console.log(error.message);
        return res.status(500).json({ msg: "Server error" });
      }
    } else {
      return res.status(400).json({});
    }
  })
  .all(methodNotAllowed);

router
  .route("/:rideId")
  .get(async (req, res) => {
    const rideId = req.params.rideId;

    try {
      // Check if rideId exist
      let ride = await rp.post(config.get("DB_API_URI").READ, {
        json: {
          model: "Ride",
          parameters: {
            rideId: rideId
          }
        }
      });

      if (ride.length == 0) {
        return res.status(204).json({ msg: "Ride does not exist" });
      }

      const retRide = {
        rideId: ride[0].rideId,
        created_by: ride[0].created_by,
        users: ride[0].users,
        timestamp: ride[0].timestamp,
        source: ride[0].source,
        destination: ride[0].destination
      };

      return res.status(200).json(retRide);
    } catch (error) {
      console.log(error.message);
      res.status(500).json({ msg: "Server error" });
    }
  })
  .post(async (req, res) => {
    if (!joiSchemas.joiValidate(joiSchemas.joinRide, req.body)) {
      return badRequest("Invalid params", req, res);
    }

    const rideId = req.params.rideId;
    const username = req.body.username;

    if (!((await rideExists({ rideId })) && (await userExists({ username }))))
      // Can this be 400 ?
      return res.status(204).json({ msg: "Not found" });

    try {
      const rides = await rp.post(config.get("DB_API_URI").READ, {
        json: {
          model: "Ride",
          parameters: { rideId }
        }
      });

      if (username === rides[0].created_by) {
        return badRequest("Invalid params", req, res);
      }

      let users = rides[0].users;
      let alreadyPresent = false;
      for (let i = 0; i < users.length; i++) {
        if (users[i] === username) {
          alreadyPresent = true;
          break;
        }
      }

      if (alreadyPresent) {
        return badRequest("Invalid params", req, res);
      }

      users.push(username);

      await rp.post(config.get("DB_API_URI").WRITE, {
        json: {
          model: "Ride",
          query: { rideId },
          update: { users },
          op: "update"
        }
      });

      return res.status(200).json({});
    } catch (error) {
      console.log(error.message);
      res.status(500).json({ msg: "Server error" });
    }
  })
  .delete(async (req, res) => {
    // Check if the ride exist
    const rideId = req.params.rideId;

    try {
      let ride = await rp.post(config.get("DB_API_URI").READ, {
        json: {
          model: "Ride",
          parameters: {
            rideId: rideId
          }
        }
      });

      if (ride.length == 0) {
        return res.status(400).json({ msg: "Ride does not exist" });
      }

      await rp.post(config.get("DB_API_URI").WRITE, {
        json: {
          model: "Ride",
          parameters: { rideId },
          op: "del"
        }
      });

      res.status(200).json({});
    } catch (error) {
      console.log(error.message);
      res.status(500).json({ msg: "Server error" });
    }
  })
  .all(methodNotAllowed);

// @route /api/v1/db/read
// @desc Database read - requires model type and parameters to be passed
router.post("/read", async (req, res) => {
  if (req.body.model && req.body.parameters) {
    let Model = null;
    const params = req.body.parameters;
    if (req.body.model === "User") {
      Model = User;
    } else if (req.body.model === "Ride") {
      Model = Ride;
    }
    try {
      const result = await Model.find(params);
      return res.status(200).json(result);
    } catch (error) {
      console.log(error.message);
      return res.status(500).json({ msg: "Server error" });
    }
  } else {
    return res.status(400).json({});
  }
});
//@route /api/v1/db/write
//@desc Database write - insert,update,delete
router.post("/write", async (req, res) => {
  // Get the model sprecified
  let Model = null;
  if (req.body.model == "User") {
    Model = User;
  } else if (req.body.model === "Ride") {
    Model = Ride;
  }
  // Check for other models later

  try {
    //  Check the type of operation specified
    switch (req.body.op) {
      case "in":
        const user = new Model(req.body.parameters);
        await user.save();
        break;
      case "del":
        await Model.findOneAndDelete(req.body.parameters);
        break;
      case "update":
        await Model.findOneAndUpdate(req.body.query, req.body.update);
        break;
    }
    console.log("DB write done");
    return res.status(200).send("DB write done");
  } catch (error) {
    console.log(error.message);
    res.status(500).send("Server error");
  }
});
