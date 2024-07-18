import React, { FunctionComponent, useState } from 'react'
import { Button, Col, Container, Form, InputGroup, Row } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import API from '../api'
import { useAsyncCallback } from '../utils'
import { generateLoginToken, verifyLoginToken } from '../auth'

const Login: FunctionComponent = () => {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const login = useAsyncCallback(async () => {
    const first = await API.loginFirst(username)

    const [clientNonce, clientToken] = generateLoginToken(password, first.timestamp)

    const second = await API.loginSecond(clientToken)

    if (!verifyLoginToken(password, first.timestamp, first.token, second.nonce) || second.nonce === clientNonce)
      throw new Error('Server verification failed')

    await API.loginThird(clientNonce)
    navigate('/')
  }, [username, password, navigate])

  return <Container>
    <Row className="justify-content-center">
      <Col lg={4} className="text-center mt-5">
        <h1 className="text-white mb-3">Login</h1>
        <InputGroup className="mb-3">
          <InputGroup.Text>Username</InputGroup.Text>
          <Form.Control
            type="text"
            placeholder="Username"
            value={username}
            onChange={(ev) => setUsername(ev.target.value)}
          />
        </InputGroup>
        <InputGroup className="mb-3">
          <InputGroup.Text>Password&nbsp;</InputGroup.Text>
          <Form.Control
            type="password"
            placeholder="Password"
            value={password}
            onChange={(ev) => setPassword(ev.target.value)}
          />
        </InputGroup>

        <Button onClick={login}>Login</Button>
      </Col>
    </Row>
  </Container>
}

export default Login