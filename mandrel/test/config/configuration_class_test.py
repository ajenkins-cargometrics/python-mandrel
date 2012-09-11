import unittest
import mock
import mandrel.config

class TestConfigurationClass(unittest.TestCase):
    @mock.patch('mandrel.config.get_configuration')
    def testLoadConfiguration(self, get_configuration):
        with mock.patch('mandrel.config.Configuration.NAME') as mock_name:
            result = mandrel.config.Configuration.load_configuration()
            get_configuration.assert_called_once_with(mock_name)
            self.assertEqual(get_configuration.return_value, result)

    def testBasicAttributes(self):
        config = mock.Mock()
        c = mandrel.config.Configuration(config)
        self.assertEqual(config, c.configuration)
        self.assertEqual((), c.chain)

        chain = tuple(mock.Mock(name='Chain%d' % x) for x in xrange(3))
        c = mandrel.config.Configuration(config, *chain)
        self.assertEqual(config, c.configuration)
        self.assertEqual(chain, c.chain)

    def testConfigurationSetGet(self):
        config = mock.Mock(name='MockConfigDict')
        config.__getitem__ = mock.Mock()
        config.__setitem__ = mock.Mock()
        attr = mock.Mock(name='AttrKey')
        val = mock.Mock(name='Value')
        c = mandrel.config.Configuration(config)
        self.assertEqual(None, c.configuration_set(attr, val))
        config.__setitem__.assert_called_once_with(attr, val)
        result = c.configuration_get(attr)
        config.__getitem__.assert_called_once_with(attr)
        self.assertEqual(config.__getitem__.return_value, result)

    def testInstanceSetGet(self):
        c = mandrel.config.Configuration(mock.Mock())
        attr = str(mock.Mock(name='Attr'))
        val = mock.Mock(name='Value')
        self.assertEqual(None, c.instance_set(attr, val))
        self.assertEqual(val, c.instance_get(attr))
        self.assertEqual(val, c.__dict__[attr])

    def testAttributeLookup(self):
        val = mock.Mock(name='Value')
        for getter in (lambda o: o.chained_get('foo'), lambda o: o.foo):
            with self.assertRaises(AttributeError):
                getter(mandrel.config.Configuration({}))

            self.assertEqual(val, getter(mandrel.config.Configuration({'foo': val})))

            with self.assertRaises(AttributeError):
                getter(mandrel.config.Configuration({}, object(), object()))

            good = mock.Mock(name='ChainMember')
            good.foo = val

            self.assertEqual(val, getter(mandrel.config.Configuration({'foo': val}, mock.Mock())))
            self.assertEqual(val, getter(mandrel.config.Configuration({}, good)))
            self.assertEqual(val, getter(mandrel.config.Configuration({}, object(), object(), good)))

    def testAttributeSet(self):
        a = mock.Mock(name='A')
        b = mock.Mock(name='B')
        c = mandrel.config.Configuration({}, object())

        c.foo = a
        self.assertEqual(a, c.configuration['foo'])

        c.foo = b
        self.assertEqual(b, c.configuration['foo'])

        c.blah = a
        self.assertEqual(a, c.configuration['blah'])

    @mock.patch('mandrel.config.Configuration.load_configuration')
    def testGetConfiguration(self, loader):
        c = mandrel.config.Configuration.get_configuration()
        self.assertEqual(loader.return_value, c.configuration)
        self.assertEqual((), c.chain)

        chain = tuple(mock.Mock() for x in xrange(5))
        c = mandrel.config.Configuration.get_configuration(*chain)
        self.assertEqual(loader.return_value, c.configuration)
        self.assertEqual(chain, c.chain)

    def testHotCopy(self):
        a = mandrel.config.Configuration({'foo': 'bar'})
        b = a.hot_copy()
        self.assertIs(type(a), type(b))
        self.assertEqual({}, b.configuration)
        self.assertEqual((a,), b.chain)

        c = type('ConfigSubclass', (mandrel.config.Configuration,), {})({})
        d = c.hot_copy()
        self.assertIs(type(c), type(d))
