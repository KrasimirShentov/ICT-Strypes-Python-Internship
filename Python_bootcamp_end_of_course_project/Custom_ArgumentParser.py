import sys

class MyNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Argument:
    def __init__(self, name, **kwargs):
        self.name = name
        self.flags = kwargs.get('flags', [])
        self.positional = kwargs.get('positional', False)
        self.type = kwargs.get('type', str)
        self.help = kwargs.get('help', '')
        self.default = kwargs.get('default')
        self.required = kwargs.get('required', False)
        self.action = kwargs.get('action', 'store')
        # self.choices = kwargs.get('choices', None)

class MutuallyExclusiveGroup:
    def __init__(self, parser, required=False):
        self.parser = parser
        self.required = required
        self.arguments = []

    def add_argument(self, *names, **kwargs):
        arg = Argument(name=names[-1], flags=names,
                       positional=False, **kwargs)
        self.arguments.append(arg)
        self.parser.arguments.append(arg)
        return arg

class ArgumentParser:
    def __init__(self, prog=None, description=None):
        self.prog = prog or sys.argv[0]
        self.description = description
        self.arguments = []
        self.mutually_exclusive_groups = []

    def add_argument(self, *names, **kwargs):
        positional = not any(n.startswith('-') for n in names)
        arg = Argument(name=names[-1], flags=names,
                       positional=positional, **kwargs)
        self.arguments.append(arg)

    def add_mutually_exclusive_group(self, required=False):
        group = MutuallyExclusiveGroup(self, required)
        self.mutually_exclusive_groups.append(group)
        return group

    def parse_args(self, args=None):
        if args is None:
            args = sys.argv[1:]

        print(args)
        namespace = dict()
        positional_args = []
        
        it = iter(args)
        for token in it:
            is_flag = False
            for arg in self.arguments:
                if not arg.positional and token in arg.flags:
                    is_flag = True
                    key = arg.name.lstrip('-').replace('-', '_')
                    
                    if arg.action == 'store_true':
                        namespace[key] = True
                    else:
                        try:
                            val = next(it)
                            namespace[key] = arg.type(val)
                        except StopIteration:
                            if arg.default is not None:
                                namespace[key] = arg.default
                            else:
                                raise ValueError(f"Missing value for {token}")
                    break
            
            if not is_flag:
                positional_args.append(token)

        print(positional_args)
        pos_it = iter(positional_args)
        for arg in self.arguments:
            if arg.positional:
                try:
                    namespace[arg.name] = arg.type(next(pos_it))
                except StopIteration:
                    if arg.required:
                        raise ValueError(f"Missing required positional argument: {arg.name}")

        try:
            extra_element = next(pos_it)
            raise ValueError(f"Unrecognised argument: {extra_element}")
        except StopIteration:
            pass
                                
        for arg in self.arguments:
            key = arg.name.lstrip('-').replace('-', '_')
            if key not in namespace:
                if arg.default is not None:
                    namespace[key] = arg.default
                elif arg.action == 'store_true':
                    namespace[key] = False
                elif arg.required and not arg.positional:
                    raise ValueError(f"Argument {arg.flags} is required")

        for group in self.mutually_exclusive_groups:
            chosen = [a for a in group.arguments if namespace.get(a.name.lstrip('-').replace('-', '_'))]
            if len(chosen) > 1:
                raise ValueError(f"arguments {', '.join(a.flags[-1] for a in chosen)} are mutually exclusive")
            if group.required and not chosen:
                raise ValueError(f"one of the arguments {', '.join(a.flags[-1] for a in group.arguments)} is required")
        
        if namespace.get("help"):
            self.print_help()
            sys.exit(0)

        return MyNamespace(**namespace)

    def print_help(self):
        lines = [f"Usage: {self.prog} [options]"]
        if self.description:
            lines.append(self.description)
        for arg in self.arguments:
            flags = ', '.join(arg.flags) if arg.flags else arg.name
            lines.append(f"{flags}\t{arg.help}")
        print('\n'.join(lines))

