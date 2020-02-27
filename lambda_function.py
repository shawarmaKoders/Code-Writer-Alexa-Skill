# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name, get_intent_name
from alexa import get_slot_data
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

from api_utils import execute_code

operator_mapping = {
    1: '>',
    2: '==',
    3: '<',
    4: '!=',
}

SKILL_NAME = "Code Writer"
WELCOME_MESSAGE = "Clickity-Click! " \
                  "I can write code while you speak. " \
                  "Now, start talking code! "
HELP_MESSAGE = "You can start talking basic Python Code. That's English, right? Come On, talk Python, talk English!"
HELP_REPROMPT = "What can I help you with?"
STOP_MESSAGE = "Goodbye!"
FALLBACK_MESSAGE = "The Code Writer skill can't help you with that.  " \
                   "It can only help you write basic code for your laziness."
FALLBACK_REPROMPT = 'What can I help you with?'
EXCEPTION_MESSAGE = "Sorry. I cannot help you with that."

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above.
sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def convert_to_variable_name(string):
    if string is None:
        return string
    return string.replace(' ', '_')


def get_indent(handler_input):
    session_attributes = handler_input.attributes_manager.session_attributes
    indent_level = int(session_attributes['indentation_level'])
    indent = '\t' * indent_level
    return indent


def update_indent(handler_input, update_value: int):
    session_attributes = handler_input.attributes_manager.session_attributes
    session_attributes['indentation_level'] = int(session_attributes['indentation_level']) + update_value
    return session_attributes['indentation_level']


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['indentation_level'] = 0
        handler_input.response_builder.speak(WELCOME_MESSAGE).ask(HELP_MESSAGE)
        return handler_input.response_builder.response


class NewIntegerIntentHandler(AbstractRequestHandler):
    """Handler for New Integer initialisation."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NewIntegerIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NewIntegerIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        integer_value = None
        variable_name = None
        output = "NewInteger it is!"
        output_speak = None
        output_display = None

        integer_value_slot_data = get_slot_data(handler_input, 'integer_value', logger=logger)
        variable_name_slot_data = get_slot_data(handler_input, 'variable_name', logger=logger)

        integer_value_string = integer_value_slot_data['value']
        if integer_value_string is None:
            logger.debug('INTEGER VALUE NOT PROVIDED!')
        else:
            integer_value = int(integer_value_string)

        variable_name_raw = variable_name_slot_data['value']
        if variable_name_raw is None:
            logger.debug('VARIABLE NAME NOT PROVIDED!')
        else:
            variable_name = convert_to_variable_name(variable_name_raw)

        if integer_value is None:
            output = "Empty variable doesn't mean anything. Please provide a value next time onwards."
        elif variable_name is None:
            output = "I'm out of options for variable names. Please provide that for me next time."
        else:
            indent = get_indent(handler_input)
            script_line = indent + "{variable_name} = {integer_value}".format(variable_name=variable_name,
                                                                              integer_value=integer_value)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output_display = script_line
            output_speak = '<voice name="Kendra">{variable_name},</voice> ' \
                           'is set!'.format(variable_name=variable_name_raw)
            output = script_line

        # if output_display is None or output_speak is None:
        #     output_display = output
        #     output_speak = output

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        return handler_input.response_builder.response


class NewListIntentHandler(AbstractRequestHandler):
    """Handler for List Intent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NewListIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NewListIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        variable_name = None
        variable_name_slot_data = get_slot_data(handler_input, 'variable_name', logger=logger)
        variable_name_raw = variable_name_slot_data['value']

        if variable_name_raw is None:
            logger.debug('VARIABLE NAME NOT PROVIDED!')
        else:
            variable_name = convert_to_variable_name(variable_name_raw)

        if variable_name is None:
            output = "I'm out of options for variable names. Please provide that for me next time."
        else:
            script_line = "{variable_name} = []".format(variable_name=variable_name)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class CreateWhileLoopIntentHandler(AbstractRequestHandler):
    """Handler for List Intent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CreateWhileLoopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CreateWhileLoopIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        variable_name = None
        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        second_variable = get_slot_data(handler_input, 'second_variable', logger=logger)['value']
        operator_slot_data = get_slot_data(handler_input, 'operator', logger=logger)

        output = ""
        if operator_slot_data['value'] is None:
            logger.debug('{operator} not provided')
            output = 'Checking Condition is Not Provided.'
            operator = ''
        else:
            operator_id = int(operator_slot_data['value_id'])
            operator = operator_mapping[operator_id]

        if first_variable is None:
            logger.debug('{first_variable} not provided')
        if second_variable is None:
            logger.debug('{second_variable} not provided')

        if (first_variable is None) and (second_variable is None):
            output += " Neither parts of checking condition provided."
        elif first_variable is None:
            output += ' First side of checking condition not provided.'
        elif second_variable is None:
            output += ' Second side of checking condition not provided.'
        else:
            indent = get_indent(handler_input)
            first_variable = convert_to_variable_name(first_variable)
            second_variable = convert_to_variable_name(second_variable)
            script_line = indent + f"while {first_variable} {operator} {second_variable}:"
            update_indent(handler_input, 1)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
            output = f"while {first_variable} {operator_slot_data['value']} {second_variable}"

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response
      
      
class ChangeItemAtIndexIntentHandler(AbstractRequestHandler):
    """Handler for changing item at index of list."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ChangeItemAtIndexIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ChangeItemAtIndexIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        second_variable = get_slot_data(handler_input, 'second_variable', logger=logger)['value']
        index_value = get_slot_data(handler_input, 'index_value', logger=logger)['value']
        output=""
        if index_value is None:
            logger.debug('{index_value} not provided')           
        if first_variable is None:
            logger.debug('{first_variable} not provided')
        if second_variable is None:
            logger.debug('{second_variable} not provided')

        if (first_variable is None) and (second_variable is None) and (index_value is None):
            output += 'All three : List name, index value and variable name not provided.'
        elif first_variable is None:
            output += ' List name not provided.'
        elif second_variable is None:
            output += ' variable which you want to add not provided.'
        else:
            script_line = f"{first_variable}[{index_value}]={second_variable}"
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class ListAppendIntentHandler(AbstractRequestHandler):
    """Handler for List Append Intent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ListAppendIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ListAppendIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        list_value = None
        variable_name = None

        list_value_slot_data = get_slot_data(handler_input, 'list_value', logger=logger)
        variable_name_slot_data = get_slot_data(handler_input, 'variable_name', logger=logger)

        list_value_string = list_value_slot_data['value']
        if list_value_string is None:
            logger.debug('LIST VALUE NOT PROVIDED!')
        else:
            list_value = list_value_string

        variable_name_raw = variable_name_slot_data['value']
        if variable_name_raw is None:
            logger.debug('VARIABLE NAME NOT PROVIDED!')
        else:
            variable_name = convert_to_variable_name(variable_name_raw)

        if list_value is None:
            output = "Empty value doesn't mean anything. Please provide a value next time onwards."
        elif variable_name is None:
            output = "I'm out of options for variable names. Please provide that for me next time."
        else:
            script_line = "{variable_name}.append({list_value})".format(variable_name=variable_name,
                                                                        list_value=list_value)
            
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class ForLoopIntentHandler(AbstractRequestHandler):
    """Handler for List Append Intent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ForLoopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ForLoopIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        starting_number = get_slot_data(handler_input, 'starting_number', logger=logger)['value']
        ending_number = get_slot_data(handler_input, 'ending_number', logger=logger)['value']

        if starting_number is None:
            logger.debug('{starting_number} NOT PROVIDED!')
        if ending_number is None:
            logger.debug('{ending_number} NOT PROVIDED!')

        if (starting_number is None) and (ending_number is None):
            output = 'You have neither defined Starting, nor Ending point for the loop'
        elif starting_number is None:
            output = 'You have not defined starting point of the loop'
        elif ending_number is None:
            output = 'You have not defined ending point of the loop'
        else:
            indent = get_indent(handler_input)
            script_line = indent + f"for i in range({starting_number}, {ending_number}+1):"
            update_indent(handler_input, 1)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class SortingListIntentHandler(AbstractRequestHandler):
    """Handler for sorting a list."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SortingListIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SortingListIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))
        
        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        
        output=""          
        if first_variable is None:
            logger.debug('{first_variable} not provided')
        
        if first_variable is None:
            output += ' List name not provided.'
        
        else:
            
            script_line = f"{first_variable}.sort()"
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
                
            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class JoiningTwoListIntentHandler(AbstractRequestHandler):
    """Handler for joining two list."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("JoiningTwoListIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In JoiningTwoIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))
        
        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        second_variable = get_slot_data(handler_input, 'second_variable', logger=logger)['value']       
        output=""
        if (first_variable is None) and (second_variable is None):
            output += 'List names not provided.'
        elif first_variable is None:
            output += ' List-1 name not provided.'
        elif second_variable is None:
            output += ' List-2 name not provided.'
        else:
            script_line =f"{first_variable}.extend({second_variable})"
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
                
            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class RemoveItemFromListIntentHandler(AbstractRequestHandler):
    """Handler for removing an item from list."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("RemoveItemIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RemoveItemFromListIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))
        
        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        second_variable = get_slot_data(handler_input, 'second_variable', logger=logger)['value']
        
        output = ""
                 
        if first_variable is None:
            logger.debug('{first_variable} not provided')
        if second_variable is None:
            logger.debug('{second_variable} not provided')

        if (first_variable is None) and (second_variable is None) :
            output += 'Both List name and variable name to be removed not provided.'
        elif first_variable is None:
            output += ' List name not provided.'
        elif second_variable is None:
            output += ' variable which you want to remove not provided.'
        else:
            
            script_line = f"{first_variable}.remove({second_variable})"
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
                
            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class ExecuteCodeIntentHandler(AbstractRequestHandler):
    """Handler for Executing code through external API"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ExecuteCodeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExecuteCodeIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))
        final_result = None

        if 'current_script_code' in session_attributes:
            code_string = session_attributes['current_script_code']
            code_string += '\nprint("It ran successfully!")'
            code_result = execute_code(code_string)
            result_string = code_result['output']
            output = ''
            if code_result['has_compilation_error']:
                output += "Your couldn't be compiled because of compilation error. "
            elif code_result['has_run_time_error']:
                output += "Your code has some errors. "
            elif len(result_string.strip()) > 0:
                output += f'Output for your code is, ' \
                    f'<emphasis level="strong">{result_string.strip()}</emphasis> '
                final_result = result_string
            output += f"Here's the URL for your executed code: {code_result['code_url']}"
        else:
            output = "You haven't entered any code to get output for. " \
                     "Please continue by speaking code!"

        logger.info(f'FINAL OUTPUT: {final_result}')

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class DecreaseIndentIntentHandler(AbstractRequestHandler):
    """Handler for Decreasing Indent in Generated code by one"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DecreaseIndent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In DecreaseIndentIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        if len(get_indent(handler_input)) > 0:
            update_indent(handler_input, -1)
            output = "Indent decreased by one."
        else:
            output = "You aren't at higher indentation level to begin with. " \
                     "Please continue by speaking code!"

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class NewIfBlockIntentHandler(AbstractRequestHandler):
    """Handler for New If Block."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NewIfBlockIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NewIfBlockIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))
        
        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        second_variable = get_slot_data(handler_input, 'second_variable', logger=logger)['value']
        operator_slot_data = get_slot_data(handler_input, 'operator', logger=logger)
        output = ""
        if operator_slot_data['value'] is None:
            logger.debug('{operator} not provided')
            output = 'Checking Condition is Not Provided.'
            operator = ''
        else:
            operator_id = int(operator_slot_data['value_id'])
            operator = operator_mapping[operator_id]
        
        if first_variable is None:
            logger.debug('{first_variable} not provided')
        if second_variable is None:
            logger.debug('{second_variable} not provided')

        if (first_variable is None) and (second_variable is None):
            output += 'Neither parts of checking condition provided.'
        elif first_variable is None:
            output += ' First side of checking condition not provided.'
        elif second_variable is None:
            output += ' Second side of checking condition not provided.'
        else:
            indent = get_indent(handler_input)
            first_variable = convert_to_variable_name(first_variable)
            second_variable = convert_to_variable_name(second_variable)
            script_line = indent + f"if {first_variable} {operator} {second_variable}:"
            update_indent(handler_input, 1)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
                
            output = f"if {first_variable} {operator_slot_data['value']} {second_variable}"

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class NewElIfBlockIntentHandler(AbstractRequestHandler):
    """Handler for New ElIf Block."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NewElIfBlockIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NewElIfBlockIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        first_variable = get_slot_data(handler_input, 'first_variable', logger=logger)['value']
        second_variable = get_slot_data(handler_input, 'second_variable', logger=logger)['value']
        operator_slot_data = get_slot_data(handler_input, 'operator', logger=logger)
        output=""
        if operator_slot_data['value'] is None:
            logger.debug('{operator} not provided')
            output = 'Checking Condition is Not Provided.'
            operator = ''
        else:
            operator_id = int(operator_slot_data['value_id'])
            operator = operator_mapping[operator_id]
        
        if first_variable is None:
            logger.debug('{first_variable} not provided')
        if second_variable is None:
            logger.debug('{second_variable} not provided')

        if (first_variable is None) and (second_variable is None):
            output += 'Neither parts of checking condition provided.'
        elif first_variable is None:
            output += ' First side of checking condition not provided.'
        elif second_variable is None:
            output += ' Second side of checking condition not provided.'
        else:
            update_indent(handler_input,-1)
            indent = get_indent(handler_input)
            first_variable = convert_to_variable_name(first_variable)
            second_variable = convert_to_variable_name(second_variable)
            script_line = indent + f"elif {first_variable} {operator} {second_variable}:"
            update_indent(handler_input, 1)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line
                
            output = f"elif {first_variable} {operator_slot_data['value']} {second_variable}"

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class NewElseBlockIntentHandler(AbstractRequestHandler):
    """Handler for New Else Block."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NewElseBlockIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NewElseBlockIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))
       
        output=""
        update_indent(handler_input, -1)
        indent = get_indent(handler_input)
        script_line = indent + "else:"
        update_indent(handler_input, 1)
        try:
            session_attributes['current_script_code'] += '\n'
            session_attributes['current_script_code'] += script_line
        except KeyError:
            session_attributes['current_script_code'] = script_line
                
            output = script_line

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


class NewStringIntentHandler(AbstractRequestHandler):
    """Handler for New String initialisation."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NewStringIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NewStringIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        string_value = None
        variable_name = None
        output = "NewString it is!"
        output_speak = None
        output_display = None

        string_value_slot_data = get_slot_data(handler_input, 'string_value', logger=logger)
        variable_name_slot_data = get_slot_data(handler_input, 'variable_name', logger=logger)

        string_value_string = string_value_slot_data['value']
        if string_value_string is None:
            logger.debug('STRING VALUE NOT PROVIDED!')
        else:
            string_value = string_value_string

        variable_name_raw = variable_name_slot_data['value']
        if variable_name_raw is None:
            logger.debug('VARIABLE NAME NOT PROVIDED!')
        else:
            variable_name = convert_to_variable_name(variable_name_raw)

        if string_value is None:
            output = "Empty variable doesn't mean anything. Please provide a value next time onwards."
        elif variable_name is None:
            output = "I'm out of options for variable names. Please provide that for me next time."
        else:
            indent = get_indent(handler_input)
            script_line = indent + "{variable_name} = {string_value}".format(variable_name=variable_name,
                                                                             string_value=string_value)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output_display = script_line
            output_speak = '<voice name="Kendra">{variable_name},</voice> ' \
                           'is set!'.format(variable_name=variable_name_raw)
            output = script_line

        # if output_display is None or output_speak is None:
        #     output_display = output
        #     output_speak = output

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class PrintStatementIntentHandler(AbstractRequestHandler):
    """Handler for Print statement initialisation."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("PrintStatementIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PrintStatementIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        print_statement = None

        print_statement_slot_data = get_slot_data(handler_input, 'print_statement', logger=logger)

        print_statement_string = print_statement_slot_data['value']
        if print_statement_string is None:
            logger.debug('Nothing provided to print')
        else:
            print_statement = print_statement_string

        if print_statement is None:
            output = "Nothing provided to print. Please let me know what to print."
        else:
            indent = get_indent(handler_input)
            script_line = indent + "print('{string_value}')".format(string_value=print_statement)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output_speak = 'Would print <voice name="Kendra">{string_value},</voice> '.format(string_value=print_statement)
            output = script_line

        # if output_display is None or output_speak is None:
        #     output_display = output
        #     output_speak = output

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class DisplayVariableIntentHandler(AbstractRequestHandler):
    """Handler for printing variables """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DisplayVariableIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In DisplayVariableIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        print_statement_variable = None

        print_statement_slot_data = get_slot_data(handler_input, 'variable_name', logger=logger)

        print_statement_string = print_statement_slot_data['value']
        if print_statement_string is None:
            logger.debug('No variable supplied to print')
        else:
            print_statement_variable = convert_to_variable_name(print_statement_string)

        if print_statement_variable is None:
            output = "No matching variable found to print. Please supply correct variable to print"
        else:
            indent = get_indent(handler_input)
            script_line = indent + "print({string_value})".format(string_value=print_statement_variable)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output_speak = 'Added print statement for variable ' \
                           '<voice name="Kendra">' \
                           '{string_value},' \
                           '</voice> '.format(string_value=print_statement_variable)
            output = script_line

        # if output_display is None or output_speak is None:
        #     output_display = output
        #     output_speak = output

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


class AddCommentIntentHandler(AbstractRequestHandler):
    """Handler for comment statements."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddCommentIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AddCommentIntentHandler")

        session_attributes = handler_input.attributes_manager.session_attributes
        logger.info('SESSION ATTRIBUTES: ' + str(session_attributes))

        print_statement = None

        print_statement_slot_data = get_slot_data(handler_input, 'comment_string', logger=logger)

        print_statement_string = print_statement_slot_data['value']
        if print_statement_string is None:
            logger.debug('No comment statement found')
        else:
            print_statement = print_statement_string

        if print_statement is None:
            output = "Unable to find comment statement"
        else:
            indent = get_indent(handler_input)
            script_line = indent + "# {string_value}".format(string_value=print_statement)
            try:
                session_attributes['current_script_code'] += '\n'
                session_attributes['current_script_code'] += script_line
            except KeyError:
                session_attributes['current_script_code'] = script_line

            output_speak = 'New comment added <voice name="Kendra">{string_value},</voice> '.format(string_value=print_statement)
            output = script_line

        # if output_display is None or output_speak is None:
        #     output_display = output
        #     output_speak = output

        handler_input.response_builder.speak(output).set_card(
            SimpleCard(SKILL_NAME, output))
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.response


# Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(NewIntegerIntentHandler())
sb.add_request_handler(NewListIntentHandler())
sb.add_request_handler(ListAppendIntentHandler())
sb.add_request_handler(ForLoopIntentHandler())
sb.add_request_handler(CreateWhileLoopIntentHandler())
sb.add_request_handler(NewStringIntentHandler())
sb.add_request_handler(SortingListIntentHandler())
sb.add_request_handler(RemoveItemFromListIntentHandler())
sb.add_request_handler(JoiningTwoListIntentHandler())
sb.add_request_handler(ExecuteCodeIntentHandler())
sb.add_request_handler(AddCommentIntentHandler())
sb.add_request_handler(ChangeItemAtIndexIntentHandler())
sb.add_request_handler(PrintStatementIntentHandler())
sb.add_request_handler(DisplayVariableIntentHandler())
sb.add_request_handler(NewIfBlockIntentHandler())
sb.add_request_handler(NewElIfBlockIntentHandler())
sb.add_request_handler(NewElseBlockIntentHandler())
sb.add_request_handler(DecreaseIndentIntentHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
# sb.add_request_handler(IntentReflectorHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# request, response logs.
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
