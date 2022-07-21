# BEE API

A small API that stores a flask of bees.

## GET BEES

```
curl localhost:4000/bees
```

## CREATE BEE

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"name":"martin"}' \
  http://localhost:4000/bees
```

## DELETE BEE

```
curl -X DELETE localhost:4000/bees/1
```
